from flask import Flask, render_template, Response, jsonify, send_file
from picamera2 import Picamera2
import io
from datetime import datetime

app = Flask(__name__)
picam2 = Picamera2()

# Configure the camera
picam2.configure(picam2.create_preview_configuration(main={"size": (320, 240)}))
picam2.start()

def generate_frames():
    while True:
        buffer = io.BytesIO()
        picam2.capture_file(buffer, format='jpeg')
        frame = buffer.getvalue()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture_image', methods=['GET'])
def capture_image():
    # Capture the image in memory instead of saving it on the Pi
    buffer = io.BytesIO()
    picam2.capture_file(buffer, format='jpeg')
    buffer.seek(0)

    # Send the image file to the client for download
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.jpg"
    return send_file(buffer, mimetype='image/jpeg', as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)