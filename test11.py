import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageSequence, ImageEnhance
import time
import threading

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Control Panel Application")
        self.geometry("800x600")

        # Create frames
        self.create_frames()

        # Create sidebar buttons
        self.create_sidebar_buttons()

        # Initialize control panel and display area
        self.create_control_panel()
        self.create_display_area()

        # Variables to control image display
        self.stop_display = False

    def create_frames(self):
        # Header frame
        self.header_frame = tk.Frame(self, height=50, bg='#61dafb')
        self.header_frame.pack(fill=tk.X)

        self.header_label = tk.Label(self.header_frame, text="Final Project", bg='#61dafb', fg='white', font=('Arial', 16, 'bold'))
        self.header_label.pack(side=tk.RIGHT, padx=20)

        # Sidebar frame
        self.sidebar_frame = tk.Frame(self, width=200, bg='#282c34', bd=2, relief='groove')
        self.sidebar_frame.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)

        # Content frame
        self.content_frame = tk.Frame(self, bg='#20232a', bd=2, relief='groove')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control panel and display area
        self.control_panel_frame = tk.Frame(self.content_frame, bg='#282c34', bd=2, relief='groove', height=150)
        self.control_panel_frame.pack(fill=tk.X, padx=5, pady=5)

        self.display_area_frame = tk.Frame(self.content_frame, bg='#20232a', bd=2, relief='groove')
        self.display_area_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_sidebar_buttons(self):
        button_style = {'bg': '#61dafb', 'fg': 'black', 'font': ('Arial', 12, 'bold')}
        self.start_camera_button = tk.Button(self.sidebar_frame, text="Start Camera", command=self.start_camera, **button_style)
        self.start_camera_button.pack(pady=10, padx=10, fill=tk.X)

        self.run_algorithm_button = tk.Button(self.sidebar_frame, text="Run Algorithm", command=self.run_algorithm, **button_style)
        self.run_algorithm_button.pack(pady=10, padx=10, fill=tk.X)

        self.adjust_brightness_button = tk.Button(self.sidebar_frame, text="Adjust Brightness", command=self.adjust_brightness, **button_style)
        self.adjust_brightness_button.pack(pady=10, padx=10, fill=tk.X)

        self.camera_preview_button = tk.Button(self.sidebar_frame, text="Camera Preview", command=self.camera_preview, **button_style)
        self.camera_preview_button.pack(pady=10, padx=10, fill=tk.X)

    def create_control_panel(self):
        self.control_label = tk.Label(self.control_panel_frame, text="Control Panel", bg='#282c34', fg='white', font=('Arial', 14, 'bold'))
        self.control_label.pack(pady=10)

    def create_display_area(self):
        self.display_label = tk.Label(self.display_area_frame, text="Display Area", bg='#20232a', fg='white', font=('Arial', 14, 'bold'))
        self.display_label.pack(pady=10)

    def start_camera(self):
        for widget in self.control_panel_frame.winfo_children():
            widget.destroy()

        fields = ["Origin X", "Origin Y", "Height", "Width", "Runtime (s)", "Exposure Time"]
        self.entries = {}

        for i, field in enumerate(fields):
            label = tk.Label(self.control_panel_frame, text=f"{field}:", bg='#282c34', fg='white')
            label.grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = tk.Entry(self.control_panel_frame, width=50)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field] = entry

        save_file_label = tk.Label(self.control_panel_frame, text="Save File Path:", bg='#282c34', fg='white')
        save_file_label.grid(row=len(fields), column=0, padx=5, pady=5, sticky='e')
        self.save_file_entry = tk.Entry(self.control_panel_frame, width=50)
        self.save_file_entry.grid(row=len(fields), column=1, padx=5, pady=5)
        tk.Button(self.control_panel_frame, text="Browse", command=self.select_save_file, bg='#61dafb', fg='black').grid(row=len(fields), column=2, padx=5, pady=5)
        self.previewButton =tk.Checkbutton(self.control_panel_frame,text="preview",bg='#61dafb', fg='black', onvalue=1, offvalue=0).grid(row=len(fields)+1, column=0, padx=5, pady=5)
        tk.Button(self.control_panel_frame, text="Submit", command=self.submit_camera_settings, bg='#61dafb', fg='black').grid(row=len(fields)+1, column=1, columnspan=3, pady=5)

    def select_save_file(self):
        save_file_path = filedialog.asksaveasfilename(defaultextension=".tiff", filetypes=[("TIFF files", "*.tiff *.tif")])
        self.save_file_entry.insert(0, save_file_path)


    def submit_camera_settings(self):
        camera_settings = {field: entry.get() for field, entry in self.entries.items()}
        previewButton =self.previewButton

        save_file_path = self.save_file_entry.get()
        if save_file_path:
            # Implement the logic to start the camera with these settings
            messagebox.showinfo("Info", f"Camera started with settings: {camera_settings}\nSave path: {save_file_path} preview {previewButton}")
            self.run_camera(camera_settings, save_file_path)
        else:
            messagebox.showerror("Error", "Please provide a save file path")

    
    def run_camera(self,camera_settings, save_file_path):
        print("camera_settings",camera_settings)


    def run_algorithm(self):
        for widget in self.control_panel_frame.winfo_children():
            widget.destroy()

        tk.Label(self.control_panel_frame, text="Select File:", bg='#282c34', fg='white').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.file_entry = tk.Entry(self.control_panel_frame, width=50)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.control_panel_frame, text="Browse", command=self.select_file, bg='#61dafb', fg='black').grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.control_panel_frame, text="Select Folder:", bg='#282c34', fg='white').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.folder_entry = tk.Entry(self.control_panel_frame, width=50)
        self.folder_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.control_panel_frame, text="Browse", command=self.select_folder, bg='#61dafb', fg='black').grid(row=1, column=2, padx=5, pady=5)

        tk.Button(self.control_panel_frame, text="Submit", command=self.submit_algorithm, bg='#61dafb', fg='black').grid(row=2, column=0, columnspan=3, pady=5)
        tk.Button(self.control_panel_frame, text="Stop", command=self.stop_algorithm, bg='#61dafb', fg='black').grid(row=3, column=0, columnspan=3, pady=5)


    def adjust_brightness(self):
        for widget in self.control_panel_frame.winfo_children():
            widget.destroy()

        tk.Label(self.control_panel_frame, text="Select File (TIFF/PNG):", bg='#282c34', fg='white').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.brightness_file_entry = tk.Entry(self.control_panel_frame, width=50)
        self.brightness_file_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.control_panel_frame, text="Browse", command=self.select_brightness_file, bg='#61dafb', fg='black').grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.control_panel_frame, text="Brightness Value:", bg='#282c34', fg='white').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.brightness_scale = ttk.Scale(self.control_panel_frame, from_=0, to=2, orient='horizontal')
        self.brightness_scale.set(1)
        self.brightness_scale.grid(row=1, column=1, padx=5, pady=5)

        self.auto_brightness_var = tk.BooleanVar()
        self.auto_brightness_check = tk.Checkbutton(self.control_panel_frame, text="Auto Brightness", variable=self.auto_brightness_var, bg='#282c34', fg='white')
        self.auto_brightness_check.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.control_panel_frame, text="Submit", command=self.submit_brightness_adjustment, bg='#61dafb', fg='black').grid(row=3, column=0, columnspan=3, pady=5)
        tk.Button(self.control_panel_frame, text="Stop", command=self.stop_algorithm, bg='#61dafb', fg='black').grid(row=4, column=0, columnspan=3, pady=5)


    def select_brightness_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("TIFF files", "*.tiff *.tif"), ("PNG files", "*.png")])
        self.brightness_file_entry.insert(0, file_path)

    def submit_brightness_adjustment(self):
        file_path = self.brightness_file_entry.get()
        brightness_value = self.brightness_scale.get()

        if file_path:
            threading.Thread(target=self.adjust_and_display_brightness, args=(file_path, brightness_value)).start()
        else:
            messagebox.showerror("Error", "Please select a file")


    def adjust_and_display_brightness(self, file_path, brightness_value):
        self.stop_display = False
        for widget in self.display_area_frame.winfo_children():
            widget.destroy()

        try:
            image = Image.open(file_path)
            self.image_sequence = [frame.copy() for frame in ImageSequence.Iterator(image)]
            self.current_image_index = 0

            for frame in self.image_sequence:
                if self.stop_display:
                    break

                if self.auto_brightness_var.get():
                    # Auto brightness logic can be more complex, here we just set it to 1.5 for demonstration
                    brightness_value = 1.5

                enhancer = ImageEnhance.Brightness(frame)
                brightened_image = enhancer.enhance(brightness_value)
                self.show_image(brightened_image)
                time.sleep(2)  # Display each image for 2 seconds
        except Exception as e:
            messagebox.showerror("Error", f"Failed to adjust brightness: {e}")


    def camera_preview(self):
        messagebox.showinfo("Info", "Camera Preview button clicked")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("TIFF files", "*.tiff *.tif")])
        self.file_entry.insert(0, file_path)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        self.folder_entry.insert(0, folder_path)


    def submit_algorithm(self):
            file_path = self.file_entry.get()
            folder_path = self.folder_entry.get()
            if file_path and folder_path:
                threading.Thread(target=self.display_images, args=(file_path,)).start()
            else:
                messagebox.showerror("Error", "Please select both file and folder")

    def display_images(self, file_path):
        self.stop_display = False
        for widget in self.display_area_frame.winfo_children():
            widget.destroy()

        try:
            image = Image.open(file_path)
            self.image_sequence = [frame.copy() for frame in ImageSequence.Iterator(image)]
            self.current_image_index = 0

            for frame in self.image_sequence:
                if self.stop_display:
                    break
                self.show_image(frame)
                time.sleep(2)  # Display each image for 2 seconds
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load images: {e}")

    def show_image(self, image):
        for widget in self.display_area_frame.winfo_children():
            widget.destroy()
        tk.Label(self.display_area_frame, text="Results displayed here...", bg='#aaa').pack(pady=10)
        img = ImageTk.PhotoImage(image)
        label = tk.Label(self.display_area_frame, image=img, bg='#20232a')
        label.image = img  # Keep a reference to avoid garbage collection
        label.pack(expand=True)
        

    def stop_algorithm(self):
        self.stop_display = True
        for widget in self.display_area_frame.winfo_children():
            widget.destroy()
        tk.Label(self.display_area_frame, text="Display Area", bg='#20232a', fg='white', font=('Arial', 14, 'bold')).pack(pady=10)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
