import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import os
import threading


class SecurityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Security System")
        self.root.geometry("800x600")

        # Variables
        self.running = False
        self.user_message = tk.StringVar()
        self.timer_minutes = tk.IntVar()
        self.timer_seconds = 0
        self.last_capture_time = 0
        self.capture_folder = "captures"
        os.makedirs(self.capture_folder, exist_ok=True)
        self.cap = cv2.VideoCapture(0)

        # Haar cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        # Initial Page Setup
        self.create_setup_page()

    def create_setup_page(self):
        """Page 1: Input message and timer."""
        self.clear_frame()

        ttk.Label(self.root, text="Enter Custom Message:", font=("Arial", 16)).pack(pady=10)
        self.message_entry = ttk.Entry(self.root, textvariable=self.user_message, font=("Arial", 14), width=30)
        self.message_entry.pack(pady=10)

        ttk.Label(self.root, text="Set Timer (minutes):", font=("Arial", 16)).pack(pady=10)
        self.timer_entry = ttk.Entry(self.root, textvariable=self.timer_minutes, font=("Arial", 14), width=10)
        self.timer_entry.pack(pady=10)

        ttk.Button(self.root, text="Start Monitoring", command=self.start_monitoring).pack(pady=20)

    def create_monitoring_page(self):
        """Page 2: Monitoring with camera feed and timer."""
        self.clear_frame()

        # Message display
        self.message_label = ttk.Label(self.root, text=self.user_message.get(), font=("Arial", 32), wraplength=700)
        self.message_label.pack(pady=10)

        # Timer display
        self.timer_label = ttk.Label(self.root, text="", font=("Arial", 20))
        self.timer_label.pack(pady=10)

        # Camera view
        self.video_label = ttk.Label(self.root)
        self.video_label.pack(pady=10)

    def start_monitoring(self):
        """Start monitoring logic."""
        if not self.user_message.get() or not self.timer_minutes.get():
            tk.messagebox.showwarning("Input Error", "Please enter both message and timer.")
            return

        # Switch to monitoring page
        self.timer_seconds = self.timer_minutes.get() * 60
        self.running = True
        self.create_monitoring_page()

        # Start monitoring thread
        threading.Thread(target=self.monitor, daemon=True).start()

    def monitor(self):
        """Monitoring with webcam feed and timeout logic."""
        start_time = time.time()
        while self.running:
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            remaining_time = self.timer_seconds - int(elapsed_time)

            # Update timer label
            if remaining_time > 0:
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                self.timer_label.config(text=f"Time Left: {minutes:02}:{seconds:02}")
            else:
                # Timeout behavior
                self.show_timeout_message()
                break

            # Capture video frame
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Detect face
            if self.detect_face(frame):
                self.save_capture(frame)

            # Display camera feed without flickering
            self.display_camera_feed(frame)

            time.sleep(0.03)  # Small delay to stabilize the GUI

        self.cap.release()

    def display_camera_feed(self, frame):
        """Update camera feed in the GUI."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(img)
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)

    def detect_face(self, frame):
        """Detect face using Haar cascade."""
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        # If a face is detected, return True
        if len(faces) > 0:
            # Check for cooldown period
            if time.time() - self.last_capture_time > 3:  # 3 seconds cooldown
                self.last_capture_time = time.time()
                return True
        return False

    def save_capture(self, frame):
        """Save captured image in the predefined folder."""
        filename = os.path.join(self.capture_folder, f"face_detected_{int(time.time())}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")

    def show_timeout_message(self):
        """Display timeout message."""
        self.running = False
        self.clear_frame()
        timeout_msg = (
            "Name: POLOK PODDAR (PROLOY)\n"
            "If urgent, call: 01770065234"
        )
        ttk.Label(self.root, text=timeout_msg, font=("Arial", 24), wraplength=700, justify="center").pack(pady=50)

    def clear_frame(self):
        """Clear all widgets from the root frame."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def close_app(self):
        """Cleanup resources before closing."""
        self.running = False
        self.cap.release()
        self.root.destroy()


# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
