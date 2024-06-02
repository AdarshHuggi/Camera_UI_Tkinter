import tkinter as tk
from tkinter import filedialog
import threading
import time
from PIL import Image, ImageTk, ImageSequence

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("Camera Application")
        self.parent.geometry("800x600")

        self.header_frame = HeaderFrame(self)
        self.header_frame.pack(side="top", fill="x")

        self.sidebar_frame = SidebarFrame(self)
        self.sidebar_frame.pack(side="left", fill="y", expand=False)

        self.display_frame = DisplayFrame(self)
        self.display_frame.pack(side="right", fill="both", expand=True)

class HeaderFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.config(height=30, bg="#007acc", relief="raised", bd=2)

        project_label = tk.Label(self, text="Test Project", font=("Arial", 16), bg="#007acc", fg="white")
        project_label.pack(pady=10)

class SidebarFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.config(width=160, bg="#003366", relief="raised", bd=2)

        self.start_camera_button = tk.Button(self, text="Start Camera", command=self.start_camera, bg="#0059b3", fg="white")
        self.start_camera_button.pack(pady=20, padx=10)

        self.run_algorithm_button = tk.Button(self, text="Run Algorithm", command=self.run_algorithm, bg="#0059b3", fg="white")
        self.run_algorithm_button.pack(pady=20, padx=10)

        self.crop_profile_button = tk.Button(self, text="Crop Profile", command=self.crop_profile, bg="#0059b3", fg="white")
        self.crop_profile_button.pack(pady=20, padx=10)

        self.brightness_button = tk.Button(self, text="Brightness", command=self.adjust_brightness, bg="#0059b3", fg="white")
        self.brightness_button.pack(pady=20, padx=10)

    def start_camera(self):
        self.parent.display_frame.show_camera_controls()

    def run_algorithm(self):
        self.parent.display_frame.show_algorithm_controls()

    def crop_profile(self):
        self.parent.display_frame.show_crop_profile_controls()

    def adjust_brightness(self):
        self.parent.display_frame.show_brightness_controls()

class DisplayFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.camera_controls_frame = None
        self.algorithm_controls_frame = None
        self.crop_profile_controls_frame = None
        self.brightness_controls_frame = None
        self.runtime_thread = None
        self.algorithm_thread = None
        self.stop_event = threading.Event()
        self.config(bg="#e6f2ff", relief="raised", bd=2)

    def show_crop_profile_controls(self):
        self.clear_display_frame()
        self.crop_profile_controls_frame = tk.Frame(self, bg="#e6f2ff")
        self.crop_profile_controls_frame.pack(pady=20, padx=20)

        file_row = tk.Frame(self.crop_profile_controls_frame, bg="#e6f2ff")
        file_label = tk.Label(file_row, text="Select File", width=15, anchor='w', bg="#e6f2ff")
        self.file_path_crop = tk.StringVar()
        file_button = tk.Button(file_row, text="Browse", command=self.pick_file_crop, bg="#0059b3", fg="white")
        file_entry = tk.Entry(file_row, textvariable=self.file_path_crop, width=30)
        file_row.pack(side="top", fill="x", pady=5)
        file_label.pack(side="left", padx=5)
        file_button.pack(side="left", padx=5)
        file_entry.pack(side="right", expand=True, fill="x")

        self.crop_submit_button = tk.Button(self.crop_profile_controls_frame, text="Submit", command=self.crop_profile_submit, bg="#0059b3", fg="white")
        self.crop_submit_button.pack(pady=20)
        
        self.crop_info_label = tk.Label(self.crop_profile_controls_frame, text="", bg="#e6f2ff")
        self.crop_info_label.pack(pady=10)

    def pick_file_crop(self):
        file_selected = filedialog.askopenfilename()
        self.file_path_crop.set(file_selected)

    def crop_profile_submit(self):
        # Perform crop profile submission
        pass

    def show_brightness_controls(self):
        self.clear_display_frame()
        self.brightness_controls_frame = tk.Frame(self, bg="#e6f2ff")
        self.brightness_controls_frame.pack(pady=20, padx=20)

        file_row = tk.Frame(self.brightness_controls_frame, bg="#e6f2ff")
        file_label = tk.Label(file_row, text="Select File", width=15, anchor='w', bg="#e6f2ff")
        self.file_path_brightness = tk.StringVar()
        file_button = tk.Button(file_row, text="Browse", command=self.pick_file_brightness, bg="#0059b3", fg="white")
        file_entry = tk.Entry(file_row, textvariable=self.file_path_brightness, width=30)
        file_row.pack(side="top", fill="x", pady=5)
        file_label.pack(side="left", padx=5)
        file_button.pack(side="left", padx=5)
        file_entry.pack(side="right", expand=True, fill="x")

        self.brightness_submit_button = tk.Button(self.brightness_controls_frame, text="Submit", command=self.adjust_brightness_submit, bg="#0059b3", fg="white")
        self.brightness_submit_button.pack(pady=20)
        
        self.brightness_info_label = tk.Label(self.brightness_controls_frame, text="", bg="#e6f2ff")
        self.brightness_info_label.pack(pady=10)

    def pick_file_brightness(self):
        file_selected = filedialog.askopenfilename()
        self.file_path_brightness.set(file_selected)

    def adjust_brightness_submit(self):
        # Perform brightness adjustment
        pass

    def show_camera_controls(self):
        self.clear_display_frame()
        self.camera_controls_frame = tk.Frame(self, bg="#e6f2ff")
        self.camera_controls_frame.pack(pady=20, padx=20)
        
        fields = ["Origin X", "Origin Y", "Height", "Width", "Runtime (s)", "Exposure Time"]
        self.entries = {}

        for field in fields:
            row = tk.Frame(self.camera_controls_frame, bg="#e6f2ff")
            label = tk.Label(row, text=field, width=15, anchor='w', bg="#e6f2ff")
            entry = tk.Entry(row, width=30)
            row.pack(side="top", fill="x", pady=5)
            label.pack(side="left", padx=5)
            entry.pack(side="right", expand=True, fill="x")
            self.entries[field] = entry

        self.folder_path = tk.StringVar()
        folder_row = tk.Frame(self.camera_controls_frame, bg="#e6f2ff")
        folder_button = tk.Button(folder_row, text="Save", command=self.pick_folder, bg="#0059b3", fg="white")
        folder_entry = tk.Entry(folder_row, textvariable=self.folder_path, width=30)
        folder_row.pack(side="top", fill="x", pady=10)
        folder_button.pack(side="left", padx=5)
        folder_entry.pack(side="right", expand=True, fill="x")

        brightness_row = tk.Frame(self.camera_controls_frame, bg="#e6f2ff")
        brightness_label = tk.Label(brightness_row, text="Brightness", width=15, anchor='w', bg="#e6f2ff")
        self.brightness_slider = tk.Scale(brightness_row, from_=0, to=100, orient=tk.HORIZONTAL, bg="#e6f2ff")
        brightness_row.pack(side="top", fill="x", pady=5)
        brightness_label.pack(side="left", padx=5)
        self.brightness_slider.pack(side="right", expand=True, fill="x")
        
        buttons_row = tk.Frame(self.camera_controls_frame, bg="#e6f2ff")
        buttons_row.pack(side="top", pady=20)
        
        self.submit_button = tk.Button(buttons_row, text="Submit", command=self.start_runtime, bg="#0059b3", fg="white")
        self.submit_button.pack(side="left", padx=10)

        self.preview_button = tk.Button(buttons_row, text="Preview Camera", command=self.preview_camera, bg="#0059b3", fg="white")
        self.preview_button.pack(side="left", padx=10)

    def pick_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def start_runtime(self):
        if self.runtime_thread and self.runtime_thread.is_alive():
            return

        # Start displaying frames
        self.runtime_thread = threading.Thread(target=self.display_frames)
        self.runtime_thread.start()

    def display_frames(self):
        # Placeholder function to display frames
        image_path = "sample_frame.jpg"
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        # Assuming there's a label to display frames
        if hasattr(self, "frame_label"):
            self.frame_label.destroy()

        self.frame_label = tk.Label(self, image=photo, bg="#e6f2ff")
        self.frame_label.image = photo  # To prevent image from being garbage collected
        self.frame_label.pack(pady=10)

    def preview_camera(self):
        # Placeholder function for previewing the camera
        self.display_frames()

    def show_algorithm_controls(self):
        self.clear_display_frame()
        self.algorithm_controls_frame = tk.Frame(self, bg="#e6f2ff")
        self.algorithm_controls_frame.pack(pady=20, padx=20)

        file_row = tk.Frame(self.algorithm_controls_frame, bg="#e6f2ff")
        file_label = tk.Label(file_row, text="Select File", width=15, anchor='w', bg="#e6f2ff")
        self.file_path_algorithm = tk.StringVar()
        file_button = tk.Button(file_row, text="Browse", command=self.pick_file_algorithm, bg="#0059b3", fg="white")
        file_entry = tk.Entry(file_row, textvariable=self.file_path_algorithm, width=30)
        file_row.pack(side="top", fill="x", pady=5)
        file_label.pack(side="left", padx=5)
        file_button.pack(side="left", padx=5)
        file_entry.pack(side="right", expand=True, fill="x")

        self.algorithm_submit_button = tk.Button(self.algorithm_controls_frame, text="Submit", command=self.run_algorithm, bg="#0059b3", fg="white")
        self.algorithm_submit_button.pack(pady=20)
        
        self.algorithm_info_label = tk.Label(self.algorithm_controls_frame, text="", bg="#e6f2ff")
        self.algorithm_info_label.pack(pady=10)

    def pick_file_algorithm(self):
        file_selected = filedialog.askopenfilename(filetypes=[("TIFF files", "*.tiff;*.tif")])
        self.file_path_algorithm.set(file_selected)

    def run_algorithm(self):
        if self.algorithm_thread and self.algorithm_thread.is_alive():
            return

        # Clear previous algorithm display
        self.clear_display_frame()

        # Start the algorithm
        self.stop_event.clear()
        self.algorithm_thread = threading.Thread(target=self.algorithm1)
        self.algorithm_thread.start()

    def algorithm1(self):
        # Read the selected TIFF file and show frames one by one
        tiff_path = self.file_path_algorithm.get()
        if not tiff_path:
            self.algorithm_info_label.config(text="No file selected")
            return

        # Open the TIFF file and iterate over frames
        try:
            with Image.open(tiff_path) as img:
                for frame in ImageSequence.Iterator(img):
                    if self.stop_event.is_set():
                        break

                    photo = ImageTk.PhotoImage(frame)
                    if hasattr(self, "frame_label"):
                        self.frame_label.destroy()

                    self.frame_label = tk.Label(self, image=photo, bg="#e6f2ff")
                    self.frame_label.image = photo
                    self.frame_label.pack(pady=10)

                    self.update_idletasks()
                    time.sleep(0.1)  # Adjust this delay as needed

            # Show particle counts (for demonstration, set to 100)
            self.algorithm_info_label.config(text="Particle Counts: 100")
        except Exception as e:
            self.algorithm_info_label.config(text=f"Error: {e}")

        # Add stop button
        self.stop_button = tk.Button(self, text="Stop", command=self.stop_algorithm, bg="#ff0000", fg="white")
        self.stop_button.pack(pady=20)

    def stop_algorithm(self):
        self.stop_event.set()
        if self.algorithm_thread:
            self.algorithm_thread.join()
        self.algorithm_info_label.config(text="Algorithm stopped")
        if hasattr(self, "frame_label"):
            self.frame_label.destroy()
        if hasattr(self, "stop_button"):
            self.stop_button.destroy()

    def clear_display_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
