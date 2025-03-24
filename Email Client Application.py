import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import messagebox, scrolledtext
from plyer import notification
import threading
import time

#Replace with email, app password, and recipient for testing
YOUR_EMAIL = ""
APP_PASSWORD = ""
TEST_RECIPIENT = ""

class EmailClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.imap_server = "imap.gmail.com"
        self.monitoring = False
        self.last_email_id = None
    
    def test_connection(self):
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email, self.password)
            with imaplib.IMAP4_SSL(self.imap_server) as mail:
                mail.login(self.email, self.password)
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)


    def send_email(self, to_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email, self.password)
                server.send_message(msg)

            return True, "Email sent successfully!"
        except Exception as e:
            return False, f"Send Error: {e}"

    def receive_latest_email(self):
        try:
            with imaplib.IMAP4_SSL(self.imap_server) as mail:
                mail.login(self.email, self.password)
                mail.select("inbox")
                status, data = mail.search(None, "ALL")
                if not data[0]:
                    return False, "No emails found."

                latest_id = data[0].split()[-1]
                status, msg_data = mail.fetch(latest_id, "(RFC822)")
                raw = msg_data[0][1]
                message = email.message_from_bytes(raw)

                subject = message["Subject"]
                sender = message["From"]
                body = ""

                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = message.get_payload(decode=True).decode()

                return True, f"From: {sender}\nSubject: {subject}\n\n{body}"
        except Exception as e:
            return False, f"Receive Error: {e}"

    def monitor_inbox(self):
        while self.monitoring:
            try:
                with imaplib.IMAP4_SSL(self.imap_server) as mail:
                    mail.login(self.email, self.password)
                    mail.select("inbox")
                    _, data = mail.search(None, "ALL")
                    if not data[0]:
                        continue

                    latest_id = data[0].split()[-1]

                    if latest_id != self.last_email_id:
                        self.last_email_id = latest_id
                        _, msg_data = mail.fetch(latest_id, "(RFC822)")
                        raw = msg_data[0][1]
                        message = email.message_from_bytes(raw)
                        notification.notify(
                            title="New Email",
                            message=f"From: {message['From']}\nSubject: {message['Subject']}",
                            timeout=5
                        )
                time.sleep(10)
            except Exception as e:
                print("Monitor error:", e)
                time.sleep(15)

class EmailClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Email Client")
        self.client = None
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Email:", font=("Times New Roman", 16)).pack()
        self.user_email_entry = tk.Entry(self.root, font=("Times New Roman", 12), width=30)
        self.user_email_entry.pack(pady=2)

        tk.Label(self.root, text="Password:", font=("Times New Roman", 16)).pack()
        self.password_entry = tk.Entry(self.root, font=("Times New Roman", 12), width=30, show="*")
        self.password_entry.pack(pady=2)

        tk.Label(self.root, text="Recipient Email:", font=("Times New Roman", 16)).pack()
        self.to_entry = tk.Entry(self.root, font=("Times New Roman", 12), width=30)
        self.to_entry.pack(pady=2)

        tk.Label(self.root, text="Subject:", font=("Times New Roman", 16)).pack()
        self.subject_entry = tk.Entry(self.root, font=("Times New Roman", 12), width=30)
        self.subject_entry.pack(pady=2)

        tk.Label(self.root, text="Message Body:", font=("Times New Roman", 16)).pack()
        self.body_text = scrolledtext.ScrolledText(self.root, width=100, height=20, font=("Times New Roman", 12))
        self.body_text.pack(pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Send Email", command=self.send_email).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Fetch Latest Email", command=self.fetch_email).pack(side=tk.LEFT, padx=10)

        self.monitor_btn = tk.Button(btn_frame, text="Start Monitoring", command=self.toggle_monitor)
        self.monitor_btn.pack(side=tk.LEFT, padx=10)

    def send_email(self):
        user_email = self.user_email_entry.get().strip()
        password = self.password_entry.get().strip()
        to_email = self.to_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.body_text.get("1.0", tk.END).strip()

        if not all([user_email, password, to_email]):
            messagebox.showerror("Error", "Email, password, and recipient are required.")
            return

        self.client = EmailClient(user_email, password)
        success, msg = self.client.send_email(to_email, subject, body)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

    def fetch_email(self):
        user_email = self.user_email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not all([user_email, password]):
            messagebox.showerror("Error", "Email and password are required.")
            return

        self.client = EmailClient(user_email, password)
        success, content = self.client.receive_latest_email()
        if success:
            messagebox.showinfo("Latest Email", content)
        else:
            messagebox.showerror("Error", content)

    def toggle_monitor(self):
        user_email = self.user_email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not all([user_email, password]):
            messagebox.showerror("Error", "Please enter email and password before starting monitoring.")
            return

        if self.client is None:
            self.client = EmailClient(user_email, password)

        if self.client.monitoring:
            self.client.stop_email_monitoring()
            self.monitor_btn.config(text="Start Monitoring")
            messagebox.showinfo("Monitoring", "Email monitoring stopped.")
        else:
            self.client.start_email_monitoring()
            self.monitor_btn.config(text="Stop Monitoring")
            messagebox.showinfo("Monitoring", "Email monitoring started.")


def test_email_client():
    print("Test Case 1: Testing connection with valid server settings")
    client = EmailClient(YOUR_EMAIL, APP_PASSWORD)
    success, message = client.test_connection()
    print(f"Result: {'Success' if success else 'Failed'} - {message}\n")

    print("Test Case 2: Testing connection with invalid server settings")
    client = EmailClient(YOUR_EMAIL, APP_PASSWORD)
    client.smtp_server = "invalid.server.com"
    success, message = client.test_connection()
    print(f"Result: {'Success' if success else 'Failed'} - {message}\n")

    print("Test Case 3: Sending email with invalid credentials")
    client = EmailClient("test@example.com", "password")
    success, message = client.send_email("recipient@example.com", "Test Subject", "This is a test email.")
    print(f"Result: {'Success' if success else 'Failed'} - {message}\n")

    print("Test Case 4: Receiving email with invalid credentials")
    client = EmailClient("test@example.com", "password")
    success, message = client.receive_latest_email()
    print(f"Result: {'Success' if success else 'Failed'} - {message}\n")

    print("Test Case 5: Sending email with empty recipient")
    client = EmailClient(YOUR_EMAIL, APP_PASSWORD)
    success, message = client.send_email("", "Test Subject", "This is a test email.")
    print(f"Result: {'Success' if success else 'Failed'} - {message}\n")

    print("Test Case 6: Sending email with empty subject")
    client = EmailClient(YOUR_EMAIL, APP_PASSWORD)
    success, message = client.send_email(TEST_RECIPIENT, "", "This is a test email.")
    print(f"Result: {'Success' if success else 'Failed'} - {message}\n")

# Uncomment to run test cases before launching GUI
test_email_client()

# Start GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = EmailClientGUI(root)
    root.mainloop()
