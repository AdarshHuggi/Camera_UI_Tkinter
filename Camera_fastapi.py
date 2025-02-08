import cv2
import base64
import numpy as np
import queue
import threading
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI()

# Camera source
video_source = 0

# Shared queues for frames and processed results
frame_queue = queue.Queue(maxsize=10)  # Captured frames
processed_queue = queue.Queue(maxsize=10)  # Processed frame metadata

# Global variables
frame_count = 0
total_particles = 0
avg_particle_size = 0
capture_thread = None
process_thread = None
camera_active = False  # Flag to control capturing
stop_event = threading.Event()


def capture_frames():
    """Capture frames from the camera and push them into the queue."""
    global camera_active
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Camera not found!")
        return

    while camera_active:
        ret, frame = cap.read()
        if ret:
            if not frame_queue.full():
                frame_queue.put(frame)  # Push frame to queue
        else:
            print("Frame capture failed.")
            break

    cap.release()


def process_frames():
    """Process frames and push metadata to the processed_queue."""
    global frame_count, total_particles, avg_particle_size

    while camera_active or not frame_queue.empty():
        try:
            frame = frame_queue.get(timeout=1)  # Get frame from queue
        except queue.Empty:
            continue

        frame_count += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        
        # Apply threshold for particle detection
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours (particles)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        total_particles = len(contours)

        # Compute average particle size
        avg_particle_size = sum(cv2.contourArea(c) for c in contours) / total_particles if total_particles > 0 else 0

        # Encode processed frame to Base64
        _, buffer = cv2.imencode('.jpg', thresh)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        # Store metadata in queue
        if not processed_queue.full():
            processed_queue.put({
                "frame_count": frame_count,
                "total_particles": total_particles,
                "avg_particle_size": avg_particle_size,
                "processed_image": frame_base64
            })


def frame_generator():
    """Continuously stream processed frames with metadata."""
    try:
        while not stop_event.is_set():
            if not processed_queue.empty():
                yield f"{processed_queue.get()}\n"
            asyncio.sleep(0.1)  # Adjust for smooth streaming
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/start_parallel_processing")
def start_parallel_processing():
    """Starts capturing and processing frames."""
    global capture_thread, process_thread, camera_active

    if camera_active:
        return JSONResponse(content={"message": "Camera is already running"}, status_code=400)

    camera_active = True
    stop_event.clear()

    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    process_thread = threading.Thread(target=process_frames, daemon=True)

    capture_thread.start()
    process_thread.start()

    return JSONResponse(content={"message": "Camera capturing and processing started"}, status_code=200)


@app.get("/stop_camera")
def stop_camera():
    """Stops capturing and ensures all captured frames are processed."""
    global camera_active, capture_thread, process_thread

    if not camera_active:
        return JSONResponse(content={"message": "Camera is not running"}, status_code=400)

    camera_active = False  # Stop capturing new frames

    if capture_thread:
        capture_thread.join()  # Wait for capture thread to finish

    if process_thread:
        process_thread.join()  # Ensure all frames are processed

    return JSONResponse(content={"message": "Camera stopped and all frames processed"}, status_code=200)


@app.get("/stream")
def stream_video():
    """Streams processed frames along with metadata."""
    if processed_queue.empty():
        raise HTTPException(status_code=500, detail="No processed frames available yet.")
    
    return StreamingResponse(frame_generator(), media_type="application/json")


@app.get("/health")
def health_check():
    """Check if the camera is accessible."""
    cap = cv2.VideoCapture(video_source)
    if cap.isOpened():
        cap.release()
        return JSONResponse(content={"status": "Camera is working"}, status_code=200)
    else:
        return JSONResponse(content={"error": "Camera not found"}, status_code=500)


@app.on_event("shutdown")
def shutdown_event():
    """Stop all threads when FastAPI shuts down."""
    global camera_active
    camera_active = False
    stop_event.set()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
