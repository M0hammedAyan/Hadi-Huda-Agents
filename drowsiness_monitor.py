# drowsiness_monitor.py (updated)
import cv2
import time
import asyncio
import threading
from playsound import playsound

class DrowsinessModel:
    def __init__(self, alarm_path="alarm.wav"):
        # Load Haar cascades (with fallback)
        try:
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'  # type: ignore
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'  # type: ignore
        except AttributeError:
            face_cascade_path = 'haarcascade_frontalface_default.xml'
            eye_cascade_path = 'haarcascade_eye.xml'

        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        self.alarm_path = alarm_path

        # state flags
        self.eyes_closed_start = None
        self.hadi_alerted = False
        self.alarm_triggered = False
        self.was_drowsy = False
        self.running = False
        self.last_alert_time = 0
        self.cooldown = 15  # seconds between full cycles

        # alarm control
        self._alarm_stop_event = threading.Event()
        self._alarm_thread = None

        # track background agent tasks so we don't spawn duplicates
        self._background_tasks = set()

    # ---------- alarm control ----------
    def _alarm_loop(self):
        """Loop the alarm sound until stop event is set."""
        try:
            while not self._alarm_stop_event.is_set():
                try:
                    playsound(self.alarm_path)
                except Exception as e:
                    # playsound may raise if audio device busy — at least keep trying
                    print(f"⚠️ playsound error: {e}")
                # small sleep to check stop event frequently
                if self._alarm_stop_event.wait(timeout=0.2):
                    break
        finally:
            # ensure alarm thread cleanup
            self._alarm_thread = None

    def start_alarm(self):
        """Start alarm in a dedicated thread that loops until stopped."""
        # if already running, do nothing
        if self._alarm_thread and self._alarm_thread.is_alive():
            return
        self._alarm_stop_event.clear()
        self._alarm_thread = threading.Thread(target=self._alarm_loop, daemon=True)
        self._alarm_thread.start()

    def stop_alarm(self):
        """Signal the alarm thread to stop."""
        self._alarm_stop_event.set()
        # optionally join a short while (non-blocking)
        if self._alarm_thread:
            # give thread a moment to exit; do not block the main loop
            pass

    # ---------- helper to schedule background async tasks ----------
    def _schedule_background(self, coro):
        """
        Schedule a coroutine to run in background using asyncio.create_task.
        Keep a reference to prevent garbage collection and to allow cancellation if needed.
        """
        try:
            task = asyncio.create_task(coro)
            self._background_tasks.add(task)

            def _on_done(t):
                self._background_tasks.discard(t)
                # log exceptions to console so they are visible
                if t.cancelled():
                    return
                exc = t.exception()
                if exc:
                    print(f"⚠️ Background task exception: {exc}")

            task.add_done_callback(_on_done)
            return task
        except Exception as e:
            print(f"⚠️ Failed to schedule background task: {e}")
            return None

    # ---------- main async monitor ----------
    async def start(self, hadi_callback=None, huda_callback=None):
        """Start video-based drowsiness monitoring with enhanced agent workflow."""
        self.running = True
        print("👁️  Enhanced Drowsiness Monitor Started (press ESC to stop)")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera not accessible.")
            return

        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    await asyncio.sleep(0.05)
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                eyes_detected = False
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h//2, x:x+w]
                    eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                    if len(eyes) >= 2:
                        eyes_detected = True
                        break

                current_time = time.time()

                if eyes_detected:
                    # Eyes reopened after drowsiness - stop alarm and trigger Huda conversation
                    if self.was_drowsy:
                        # stop the physical alarm
                        if self.alarm_triggered:
                            self.stop_alarm()
                            self.alarm_triggered = False

                        # schedule huda callback in background so we don't block frame loop
                        if huda_callback:
                            self._schedule_background(huda_callback())

                        self.was_drowsy = False
                        self.hadi_alerted = False

                    # Reset timers / state
                    self.eyes_closed_start = None
                    status_text = "Eyes: OPEN"
                    color = (0, 255, 0)
                else:
                    # eyes not detected
                    if self.eyes_closed_start is None:
                        self.eyes_closed_start = current_time

                    closed_duration = current_time - self.eyes_closed_start
                    status_text = f"Eyes: CLOSED ({closed_duration:.1f}s)"
                    color = (0, 0, 255)

                    # Step 1: Hadi alert at ~2 seconds (non-blocking)
                    if closed_duration > 2.0 and not self.hadi_alerted:
                        if current_time - self.last_alert_time > self.cooldown:
                            self.hadi_alerted = True
                            self.was_drowsy = True
                            print("🚨 2s threshold! Scheduling Hadi wake-up (background task)...")
                            if hadi_callback:
                                # schedule the callback — do NOT await
                                self._schedule_background(hadi_callback())

                    # Step 2: physical alarm at ~5 seconds (looping alarm until eyes open)
                    if closed_duration > 5.0 and not self.alarm_triggered:
                        self.alarm_triggered = True
                        self.last_alert_time = current_time
                        print("🔔 5s threshold! Starting physical alarm (looping)...")
                        self.start_alarm()

                # Display status overlay
                if self.hadi_alerted and not eyes_detected:
                    status_text += " - HADI ACTIVE"

                cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                cv2.imshow("Enhanced Fatigue Detection", frame)

                # ESC to exit
                if cv2.waitKey(1) & 0xFF == 27:
                    self.running = False

                # small sleep so loop yields to asyncio
                await asyncio.sleep(0.05)
        finally:
            # cleanup on exit
            if self.alarm_triggered:
                self.stop_alarm()
            cap.release()
            cv2.destroyAllWindows()
            print("🛑 Enhanced Drowsiness Monitor Stopped.")
