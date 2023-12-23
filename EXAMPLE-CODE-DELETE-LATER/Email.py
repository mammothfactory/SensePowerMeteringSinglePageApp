import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
# THIS DOES NTO WORK ON GMAIL 
# https://support.google.com/accounts/answer/6010255?sjid=13720257961439252325-NA#zippy=%2Cif-less-secure-app-access-is-on-for-your-account
# https://myaccount.google.com/lesssecureapps?pli=1&rapt=AEjHL4MWcwLHSAVnfE9svUWDfcLFvMtpgWsxFpbCQXV1mXoGSxOG_2HG-ldIKEoG80u5mTzPmio7DE-A3XalEn_bjw0L5jxm8Q

class Email:
    
    def send_email(sender_email, sender_password, receiver_email, subject, body, file_path):
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Add body to the email
        msg.attach(MIMEBase('text', 'plain'))
        msg.attach(MIMEBase('text', 'plain').set_payload(body))

        # Attach the .db file
        with open(file_path, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{file_path}"')
        msg.attach(part)

        # Send the email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
            
if __name__ == "__main__":
    
    senderEmail = 'blaze.mfc.us@gmail.com'
    senderPassword = 'MammothTusk@42'
    receiverEmail = 'blazes@mfc.us'
    subject = 'Daily TimeReport.db file'
    body = 'Please see attached TimeReport.db file'
    filepath = 'C:/Users/Framecad/TimeTracker/TimeReport.db'
  
    Email.send_email(senderEmail, senderPassword, receiverEmail, subject, body, filepath)
