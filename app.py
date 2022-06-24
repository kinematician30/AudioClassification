from datetime import time
from time import sleep
import imghdr
from helpers import File_Manager, Predictor
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename


app = Flask(__name__)
file_manager = File_Manager()

app.config['MAX_CONTENT_LENGTH'] = 2000000 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS']  = ['.jpg', '.png', '.gif','.exe','.mp3', '.wav', '.m4a']
app.config['UPLOAD_PATH'] = 'uploads'
app.config['STATIC_PATH'] = 'static'
app.config['MODEL_PATH']  = 'model'

model = 'audio_classification.h5'
label_encoder = 'label_encoder.joblib'

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/')
def index():

    track_available = file_manager.get_avalable_track(app.config['UPLOAD_PATH'])
    track_data      = file_manager.get_track_details(track_available) # get the first value in the list of tracks

    return render_template('index.html', track = track_data )

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        print(file_ext)
        # if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
        #         file_ext != validate_image(uploaded_file.stream):
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return "Invalid image", 400

        file_manager.delete_all_files(os.path.join(app.config['UPLOAD_PATH']))
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

        make_prediction(filename=filename)

    return redirect(url_for('index'))

def make_prediction(filename):
    

    predictor = Predictor(
                        os.path.join(app.config['MODEL_PATH'], model),
                        os.path.join(app.config['MODEL_PATH'], label_encoder),
                        os.path.join(app.config['UPLOAD_PATH'], filename)
                        )

    genre = predictor.predict_genre()[0]

    with open(os.path.join(app.config['UPLOAD_PATH'], "genre"), 'w') as genre_file:
        genre_file.write(genre)

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/static_files/<filename>')
def static_files(filename):
    return send_from_directory(app.config['STATIC_PATH'], filename)

if __name__ == '__main__':
    app.run(debug=True)