from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from twilio.rest import Client
import boto3

# Initialize the Flask app
app = Flask(__name__)

# Configure the app to allow file uploads
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Max upload size: 5 MB
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png']
app.config['UPLOAD_PATH'] = 'uploads'

# Initialize the AWS S3 client
client = Client(account_sid, auth_token)

# Initialize the AWS S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name=aws_region_name)


@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Get the user's full name, phone number and uploaded file
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        uploaded_file = request.files['file']
        content_type = uploaded_file.content_type

        # Generate a secure filename
        filename = secure_filename(uploaded_file.filename)

        # Upload the file to S3
        s3.upload_fileobj(uploaded_file, s3_bucket_name,
                          filename, ExtraArgs={'ContentType': content_type})

        # Get the public URL of the uploaded file
        object_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{filename}?Content-Type={content_type}"

        # Send an MMS message with Twilio
        client.messages.create(
            body=f"{full_name} - {phone_number}",
            media_url=[object_url],
            from_='+18339722734',
            to='+12019235301'
        )

        return render_template('success.html')
    else:
        if request.method == 'GET':
            return render_template('form.html')
        else:
            return render_template('failure.html')


if __name__ == '__main__':
    app.run(debug=True)
