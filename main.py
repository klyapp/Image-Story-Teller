import os
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import cv2
import random
import numpy as np
from keras.applications.mobilenet import MobileNet, preprocess_input
from keras.preprocessing import image
from io import BytesIO

app = Flask(__name__)

# Path to the directory where uploaded files will be saved
upload_folder = 'D:\\image_story_teller_web'

# Load the pre-trained MobileNet model
model = MobileNet(weights='imagenet')

def preprocess_image(frame):
    # Resize the frame to 224x224 pixels
    frame_resized = cv2.resize(frame, (224, 224))
    # Convert the frame to an array and preprocess it for MobileNet
    img_array = image.img_to_array(frame_resized)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array_expanded_dims)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file is present in the request
        if 'video' not in request.files:
            return jsonify({"error": "File not found"}), 400
        file = request.files['video']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        if file:
            # Save the file to the upload folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Extract a random frame from the video
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return jsonify({"error": "Could not open video file"}), 500
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            random_frame = random.randint(0, frame_count - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
            success, frame = cap.read()
            cap.release()

            if success:
                # Preprocess the image for MobileNet
                processed_image = preprocess_image(frame)
                # Get predictions from the model
                predictions = model.predict(processed_image)
                # Convert predictions to a readable format (e.g., class labels)
                predicted_class = np.argmax(predictions, axis=-1)
                
                # Encode the image as JPEG and send it to the user
                _, buffer = cv2.imencode('.jpg', frame)
                io_buf = BytesIO(buffer)
                return send_file(io_buf, mimetype='image/jpeg', as_attachment=True, download_name='prediction.jpg')
                
            else:
                return jsonify({"error": "Error extracting frame from video"}), 500
        else:
            return jsonify({"error": "Error uploading file"}), 400
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
