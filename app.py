from flask import Flask, render_template, request, redirect, url_for, send_file
import boto3
import mysql.connector

app = Flask(__name__, static_folder='static')

# AWS S3 credentials
AWS_ACCESS_KEY = '############'
AWS_SECRET_KEY = '############'
S3_BUCKET = 's3awsstorageinstance'

# RDS database credentials
DB_HOST = 'mydb.cu0cmwngbm5d.us-east-1.rds.amazonaws.com'
DB_USER = '######'
DB_PASSWORD = '#####'
DB_NAME = 'seproject'

# Initialize S3 and RDS clients
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
db = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = db.cursor()

# Home route
@app.route('/')
def index():
    # Fetch file details from the database
    cursor.execute("SELECT filename FROM files")
    files = cursor.fetchall()
    return render_template('index.html', files=files)

# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    # Upload file to S3
    s3.upload_fileobj(file, S3_BUCKET, file.filename)

    # Save file details to the database
    cursor.execute("INSERT INTO files (filename) VALUES (%s)", (file.filename,))
    db.commit()

    return redirect(url_for('index'))

# File download route
@app.route('/download/<filename>')
def download_file(filename):
    # Retrieve file from S3
    s3.download_file(S3_BUCKET, filename, filename)

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    # Create the 'files' table if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS files (id INT AUTO_INCREMENT PRIMARY KEY, filename VARCHAR(255) NOT NULL)")
    db.commit()

    app.run(host='0.0.0.0', port=8000)
