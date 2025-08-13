from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
UPI_ID = os.getenv("UPI_ID")

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def send_email(subject, body, attachments):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = GMAIL_ADDRESS
    msg['Subject'] = subject
    msg.attach(MIMEBase('application', 'octet-stream'))

    for file_path in attachments:
        part = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
    server.sendmail(GMAIL_ADDRESS, GMAIL_ADDRESS, msg.as_string())
    server.quit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/print-details')
def print_details():
    return render_template('print_details.html')

@app.route('/upload-files', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        file = request.files['file']
        file_path = None
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            send_email("New STUROX Order - File Upload", "A file was uploaded.", [file_path])
        return redirect(url_for('delivery_point'))
    return render_template('upload_files.html')

@app.route('/delivery-point', methods=['GET', 'POST'])
def delivery_point():
    if request.method == 'POST':
        return redirect(url_for('order_details'))
    return render_template('delivery_point.html')

@app.route('/order-details', methods=['GET', 'POST'])
def order_details():
    if request.method == 'POST':
        bw_pages = int(request.form.get('bw_pages', 0))
        color_pages = int(request.form.get('color_pages', 0))
        total_price = bw_pages * 1 + color_pages * 3
        return render_template('payment_details.html', total_price=total_price, upi_id=UPI_ID)
    return render_template('order_details.html')

@app.route('/payment-details')
def payment_details():
    return render_template('payment_details.html', total_price=0, upi_id=UPI_ID)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
