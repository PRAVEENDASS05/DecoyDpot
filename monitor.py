import time
import os
import getpass
import socket
import sqlite3
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import smtplib
import cv2

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


# ======================================================
# DATABASE
# ======================================================

DB_PATH = "honeypot_logs.db"


# ======================================================
# INITIALIZE DATABASE
# ======================================================

def init_db():

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.execute("""

    CREATE TABLE IF NOT EXISTS logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        timestamp TEXT,

        username TEXT,

        hostname TEXT,

        ip TEXT,

        event_type TEXT,

        file_path TEXT

    )

    """)

    conn.commit()

    return conn


# ======================================================
# WEBCAM CAPTURE
# ======================================================

def capture_webcam(event_type):

    try:

        # Create evidence folder
        if not os.path.exists("evidence"):

            os.makedirs("evidence")

        # Open webcam
        camera = cv2.VideoCapture(0)

        # Check webcam opened
        if not camera.isOpened():

            print("❌ Webcam not detected")

            return None

        # Wait for webcam initialization
        time.sleep(2)

        # Capture frame
        success, frame = camera.read()

        if success:

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            image_path = f"evidence/{event_type}_{timestamp}.jpg"

            cv2.imwrite(image_path, frame)

            print("\n📸 Webcam Image Captured")

            print("Saved :", image_path)

            camera.release()

            return image_path

        else:

            print("❌ Failed to capture webcam image")

            camera.release()

            return None

    except Exception as e:

        print("❌ Webcam Error :", e)

        return None


# ======================================================
# EMAIL ALERT WITH IMAGE
# ======================================================

def send_email_alert(

    event_type,
    file_path,
    username,
    image_path

):

    sender = "praveendass.a.ciet@gmail.com"

    receiver = "praveendass.a.ciet@gmail.com"

    app_password = "veop bosy bupt yazr"

    subject = "🚨 Honeypot Security Alert"

    body = f"""

Honeypot Alert Detected!

====================================

Event Type : {event_type}

Affected File : {file_path}

Triggered By : {username}

Time : {datetime.now()}

====================================

Webcam evidence attached.

"""

    try:

        msg = MIMEMultipart()

        msg["From"] = sender

        msg["To"] = receiver

        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # Attach webcam image
        if image_path and os.path.exists(image_path):

            with open(image_path, "rb") as attachment:

                part = MIMEBase(
                    "application",
                    "octet-stream"
                )

                part.set_payload(
                    attachment.read()
                )

            encoders.encode_base64(part)

            part.add_header(

                "Content-Disposition",

                f"attachment; filename={os.path.basename(image_path)}"

            )

            msg.attach(part)

        # Send Mail
        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            sender,
            app_password
        )

        server.sendmail(

            sender,

            receiver,

            msg.as_string()

        )

        server.quit()

        print("📧 Email Alert Sent")

    except Exception as e:

        print("❌ Email Error :", e)


# ======================================================
# HONEYPOT HANDLER
# ======================================================

class HoneypotHandler(FileSystemEventHandler):

    def __init__(self):

        self.conn = init_db()

        self.last_event = ""

        self.last_time = 0

    # ==================================================
    # SAVE LOG EVENT
    # ==================================================

    def log_event(self, event_type, path):

        current_time = time.time()

        event_key = f"{event_type}:{path}"

        # Prevent duplicate spam logs
        if (

            event_key == self.last_event

            and current_time - self.last_time < 1

        ):

            return

        self.last_event = event_key

        self.last_time = current_time

        username = getpass.getuser()

        hostname = socket.gethostname()

        ip = socket.gethostbyname(hostname)

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Save into database
        self.conn.execute(

            "INSERT INTO logs VALUES (NULL,?,?,?,?,?,?)",

            (
                timestamp,
                username,
                hostname,
                ip,
                event_type,
                path
            )

        )

        self.conn.commit()

        # Console alert
        print("\n🚨 HONEYPOT ALERT 🚨")

        print("Event :", event_type)

        print("File  :", path)

        print("User  :", username)

        print("Host  :", hostname)

        print("IP    :", ip)

        print("Time  :", timestamp)

        print("--------------------------------")

        # ==============================================
        # CAPTURE WEBCAM
        # ==============================================

        image_path = capture_webcam(
            event_type
        )

        # ==============================================
        # SEND EMAIL WITH IMAGE
        # ==============================================

        send_email_alert(

            event_type,

            path,

            username,

            image_path

        )

    # ==================================================
    # FILE CREATED / COPIED
    # ==================================================

    def on_created(self, event):

        if not event.is_directory:

            print("\nDEBUG CREATED EVENT")

            print("FILE :", event.src_path)

            self.log_event(

                "CREATED/COPIED",

                event.src_path

            )

    # ==================================================
    # FILE MODIFIED
    # ==================================================

    def on_modified(self, event):

        if not event.is_directory:

            print("\nDEBUG MODIFIED EVENT")

            print("FILE :", event.src_path)

            self.log_event(

                "MODIFIED",

                event.src_path

            )

    # ==================================================
    # FILE DELETED
    # ==================================================

    def on_deleted(self, event):

        if not event.is_directory:

            print("\nDEBUG DELETED EVENT")

            print("FILE :", event.src_path)

            self.log_event(

                "DELETED",

                event.src_path

            )

    # ==================================================
    # FILE MOVED / CUT / RENAME
    # ==================================================

    def on_moved(self, event):

        if not event.is_directory:

            print("\nDEBUG MOVED EVENT")

            print("FROM :", event.src_path)

            print("TO   :", event.dest_path)

            moved_text = f"""

FROM:
{event.src_path}

TO:
{event.dest_path}

"""

            self.log_event(

                "MOVED/CUT/RENAMED",

                moved_text

            )


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    path = "./honeypot"

    # Create honeypot folder automatically
    if not os.path.exists(path):

        os.makedirs(path)

    observer = Observer()

    event_handler = HoneypotHandler()

    observer.schedule(

        event_handler,

        path,

        recursive=True

    )

    observer.start()

    print("\n🛡 Honeypot Monitoring Started")

    print("📂 Monitoring Folder :", path)

    print("⚡ Waiting for suspicious activity...\n")

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        observer.stop()

    observer.join()