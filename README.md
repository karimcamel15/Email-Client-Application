📧 **Python Email Client – Project Summary**
This project is a Python-based email client application that allows users to **send, receive, and monitor emails** using their Gmail account. It combines core networking concepts with a clean graphical user interface built using **Tkinter**, and includes **push notifications** using **Plyer**.

✅ **Core Features**
- **Send Emails**: Users can enter their email, app password, recipient address, subject, and message body, then click "Send Email" to send a message using the **SMTP** protocol. 
- **Receive Latest Email**: The "Fetch Latest Email" button retrieves and displays the most recent message from the user's inbox using the **IMAP** protocol.
- **Real-Time Email Monitoring**: With the "Start Monitoring" button, the app checks the inbox in the background and displays a **desktop notification** when a new email is received. Monitoring can be stopped at any time.

🧰 **Technologies Used**
- **Python 3**
- `smtplib` – for sending emails (SMTP)
- `imaplib` – for receiving emails (IMAP)
- `email` – for parsing and creating email content
- `tkinter` – for GUI
- `plyer` – for system notifications
- `threading` – to allow background email checking

🧪 **Testing and Validation**
A set of automated test cases was included to validate:
- Sending with invalid credentials
- Receiving with invalid credentials
- Sending with empty fields
- Sending with missing subjects
- Ensuring the app handles errors gracefully

🔐 **Security Notes**
- The app uses **Gmail App Passwords** instead of real user passwords for secure authentication.
- User credentials are not stored.

📂 **Usage**
1. Install dependencies:
   ``pip install plyer``
2. Run the script:
3. Enter your Gmail and App Password, and start sending and monitoring emails easily from the GUI.
