# drowsiness_monitor.py — Non-blocking Drowsiness + Agent Integration

import cv2
import time
import asyncio
import threading
from playsound import playsound

class DrowsinessModel:
    def __init__(self, alarm_path="alarm.wav"):
        try:
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'  # type: ignore
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'  # type: ignore
        except AttributeError:
            face_cascade_path = 'haarcascade_frontalface_default.xml'
            eye_cascade_path = 'haarcascade_eye.xml'

        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        self.alarm_path = alarm_path

        # States
        self.eyes_closed_start = None
        self.hadi_alerted = False
        self.alarm_triggered = False
        self.was_drowsy = False
        self.running = False
        self.last_alert_time = 0
        self.cooldown = 15  # seconds between full detection cycles

    def play_alarm(self):
        """Play alarm sound in a background thread."""
        def _play():
            try:
                playsound(self.alarm_path)
            except Exception as e:
                print(f"⚠️ Alarm failed: {e}")
        threading.Thread(target=_play, daemon=True).start()

    async def start(self, hadi_callback=None, huda_callback=None):
        """Start non-blocking drowsiness detection with AI agent triggers."""
        self.running = True
        print("👁️  Drowsiness Monitor (non-blocking) started — press ESC to exit.")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera not accessible.")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.05)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            eyes_detected = False
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y + h // 2, x:x + w]
                eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                if len(eyes) >= 2:
                    eyes_detected = True

            current_time = time.time()

            if eyes_detected:
                # Eyes reopened → trigger Huda empathetic follow-up
                if self.was_drowsy:
                    print("👀 Eyes reopened — starting Huda conversation.")
                    self.was_drowsy = False
                    if huda_callback:
                        # Non-blocking — allow OpenCV to continue
                        asyncio.create_task(huda_callback())

                # Reset detection state
                self.eyes_closed_start = None
                self.hadi_alerted = False
                self.alarm_triggered = False
                status_text = "Eyes: OPEN"
                color = (0, 255, 0)

            else:
                # Eyes closed detection
                if self.eyes_closed_start is None:
                    self.eyes_closed_start = current_time

                closed_duration = current_time - self.eyes_closed_start
                status_text = f"Eyes: CLOSED ({closed_duration:.1f}s)"
                color = (0, 0, 255)

                # Step 1: Trigger Hadi at 2s
                if closed_duration > 2.0 and not self.hadi_alerted:
                    if current_time - self.last_alert_time > self.cooldown:
                        self.hadi_alerted = True
                        self.was_drowsy = True
                        print("🚨 2s threshold — Hadi alert triggered!")
                        if hadi_callback:
                            asyncio.create_task(hadi_callback())

                # Step 2: Trigger alarm at 5s
                elif closed_duration > 5.0 and not self.alarm_triggered:
                    self.alarm_triggered = True
                    self.last_alert_time = current_time
                    print("🔔 5s threshold — alarm triggered.")
                    self.play_alarm()

            # Display camera feed
            if self.hadi_alerted and not eyes_detected:
                status_text += " — HADI ACTIVE"
            cv2.putText(frame, status_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.imshow("Driver Drowsiness Monitor", frame)

            # Press ESC to exit
            if cv2.waitKey(1) & 0xFF == 27:
                self.running = False

            await asyncio.sleep(0.05)

        cap.release()
        cv2.destroyAllWindows()
        print("🛑 Drowsiness Monitor stopped.")
