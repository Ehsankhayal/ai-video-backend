from flask import Flask, request, send_file, render_template
from gtts import gTTS
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text')
    resolution = request.form.get('resolution', '720p')
    image = request.files.get('image')

    if not text or not image:
        return "Missing text or image", 400

    # Save image
    filename = secure_filename(image.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    # Create audio
    tts = gTTS(text)
    audio_path = os.path.join(OUTPUT_FOLDER, 'audio.mp3')
    tts.save(audio_path)

    # Output video
    output_video_path = os.path.join(OUTPUT_FOLDER, 'output.mp4')
    resolution_map = {
        '360p': '640x360',
        '720p': '1280x720',
        '1080p': '1920x1080'
    }
    size = resolution_map.get(resolution, '1280x720')

    command = [
        'ffmpeg',
        '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-vf', f'scale={size}',
        output_video_path
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return send_file(output_video_path, as_attachment=True)
    except subprocess.CalledProcessError as e:
        return f"Error creating video: {e.stderr}", 500
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Debug template folder
    print(f"Template folder: {app.template_folder}")
    print(f"Template folder exists: {os.path.exists(app.template_folder)}")
    if os.path.exists('templates'):
        print(f"Templates directory contents: {os.listdir('templates')}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)