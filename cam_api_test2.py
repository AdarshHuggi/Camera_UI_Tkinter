import cv2
import base64
import numpy as np
import queue
import threading
import asyncio
import sqlite3
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

# FastAPI setup
app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Camera source
video_source = 0

# Shared queues
frame_queue = queue.Queue()  # Captured frames
processed_queue = queue.Queue()  # Processed frame metadata

# Global variables
frame_count = 0
total_particles = 0
avg_particle_size = 0
capture_thread = None
process_thread = None
camera_active = False
stop_event = threading.Event()
video_writer = None

# Video settings
frame_width = 640
frame_height = 480
fps = 20
output_video_path = "output2.avi"

# Database setup
DB_PATH = "frames_data.db"

def create_database():
    """Create tables in SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_particle_counter_table = """
    CREATE TABLE IF NOT EXISTS particle_counter (
        frame_name TEXT NOT NULL,
        min INTEGER,
        max INTEGER,
        particle_count INTEGER,
        datetime TEXT
    );
    """
    
    create_frame_details_table = """
    CREATE TABLE IF NOT EXISTS frame_details (
        frame_name TEXT NOT NULL,
        fps INTEGER,
        file_name TEXT,
        datetime TEXT
    );
    """

    cursor.execute(create_particle_counter_table)
    cursor.execute(create_frame_details_table)
    conn.commit()
    conn.close()

# Call to create tables on startup
create_database()


def insert_particle_data(frame_name, min_val, max_val, particle_count):
    """Insert particle data into SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO particle_counter (frame_name, min, max, particle_count, datetime)
        VALUES (?, ?, ?, ?, ?)
    """, (frame_name, min_val, max_val, particle_count, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def insert_frame_details(frame_name, fps, file_name):
    """Insert frame details into SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO frame_details (frame_name, fps, file_name, datetime)
        VALUES (?, ?, ?, ?)
    """, (frame_name, fps, file_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def start_video_writer():
    """Initialize video writer for saving processed frames."""
    global video_writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height), False)


def capture_frames():
    """Capture frames from the camera and push them into the queue."""
    global camera_active
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        logging.error("Camera not found!")
        return

    while camera_active:
        ret, frame = cap.read()
        if ret:
            if not frame_queue.full():
                frame_queue.put(frame)
                print("Frame captured.",frame_queue.qsize())
        else:
            logging.warning("Frame capture failed.")
            break

    cap.release()


def process_frames():
    """Process frames, save video, and push metadata to the queue."""
    global frame_count, total_particles, avg_particle_size, video_writer

    start_video_writer()

    while camera_active or not frame_queue.empty():
        try:
            frame = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        frame_count += 1
        frame_name = f"Frame_{frame_count}"
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply threshold for particle detection
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        total_particles = len(contours)

        # Compute min, max, and avg particle size
        particle_sizes = [cv2.contourArea(c) for c in contours]
        min_particle_size = min(particle_sizes) if particle_sizes else 0
        max_particle_size = max(particle_sizes) if particle_sizes else 0
        avg_particle_size = sum(particle_sizes) / total_particles if total_particles > 0 else 0

        # Save processed frame to video file
        if video_writer:
            video_writer.write(thresh)

        # Store in database
        insert_particle_data(frame_name, min_particle_size, max_particle_size, total_particles)
        insert_frame_details(frame_name, fps, output_video_path)

        # Encode processed frame
        _, buffer = cv2.imencode('.jpg', thresh)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        if not processed_queue.full():
            processed_queue.put({
                "frame_name": frame_name,
                "frame_count": frame_count,
                "total_particles": total_particles,
                "min_particle_size": min_particle_size,
                "max_particle_size": max_particle_size,
                "avg_particle_size": avg_particle_size,
                "processed_image": frame_base64
            })

    if video_writer:
        video_writer.release()
        video_writer = None


async def frame_generator():
    """Continuously stream processed frames."""
    while not stop_event.is_set():
        try:
            if not processed_queue.empty():
                yield f"{processed_queue.get()}\n"
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Streaming error: {e}")
            logging.error(f"Streaming error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


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
    """Stops capturing and processes remaining frames."""
    global camera_active, capture_thread, process_thread, video_writer

    if not camera_active:
        return JSONResponse(content={"message": "Camera is not running"}, status_code=400)

    camera_active = False

    if capture_thread:
        capture_thread.join()
    if process_thread:
        process_thread.join()

    if video_writer:
        video_writer.release()
        video_writer = None

    return JSONResponse(content={"message": "Camera stopped and all frames processed"}, status_code=200)


@app.get("/stream")
async def stream_video():
    """Streams processed frames."""
    if processed_queue.empty():
        logging.error("No processed frames available yet.")
        raise HTTPException(status_code=404, detail="No processed frames available yet.")

    return StreamingResponse(frame_generator(), media_type="application/json")


@app.get("/health")
def health_check():
    """Check camera status."""
    cap = cv2.VideoCapture(video_source)
    if cap.isOpened():
        cap.release()
        return JSONResponse(content={"status": "Camera is working"}, status_code=200)
    else:
        return JSONResponse(content={"error": "Camera not found"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
