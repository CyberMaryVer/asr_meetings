import numpy as np
import os
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
import time
from urllib.request import urlretrieve
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = "secret key"

ALLOWED_EXTENSIONS = {'txt', 'docx', 'doc', 'md'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    # return render_template('test.html', filename='static/images/yolo.png')
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # deep learning
        try:
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img_inp = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            img_inp = png2rgb(img_inp)
            r = main(img_inp, net, filename, precision=.5, high_quality=False)
            time.sleep(4)
            if r:
                flash('Image successfully uploaded and recognized')
            else:
                flash('There are no objects known to the neural network in the image')
        except Exception as ex:
            flash('Unknown error with the image\n')
            print(ex)
        return render_template('upload.html', filename=filename)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    flash('You can save image by clicking on it')
    time.sleep(4)
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='images/' + filename), code=301)


@app.route('/test/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)

    # For debugging
    print(f"Image url {name}")

    response = {}

    # Check if user sent an url
    if not name:
        response["ERROR"] = "no url found"
    # Valid url
    else:
        try:
            # get image
            testpath = "static/images/web_test.jpg"
            urlretrieve(name, testpath)
            img_inp = cv2.imread(testpath, cv2.IMREAD_UNCHANGED)
            print(name)
            img_inp = png2rgb(img_inp)
            img_shape = img_inp.shape
            print(img_shape)

            # recognize image
            r = main(img_inp, net, 'web_test.jpg', precision=.4, high_quality=False)
            # time.sleep(2)
            if not r:
                response["MESSAGE"] = "No objects found. Try to reduce precision parameter"
                return response
            time.sleep(4)  # to avoid 'request timeout

            # return image
            img_out = Image.open("static/images/web_test.jpg")
            img_out = np.array(img_out.getdata()).tolist()
            return {"image": img_out, "shape": img_shape}

        except Exception as ex:
            response["MESSAGE"] = f"Url {name} is invalid"
            print(ex)
            return response


if __name__ == '__main__':
    # test = cv2.imread('templates/chess.jpg', cv2.IMREAD_UNCHANGED)

    port = os.environ.get('PORT')
    if port:
        # 'PORT' variable exists - running on Heroku, listen on external IP and on given by Heroku port
        app.run(host='0.0.0.0', port=int(port))

    else:
        # 'PORT' variable doesn't exist, running not on Heroku, presumably running locally, run with default
        #   values for Flask (listening only on localhost on default Flask port)
        app.run()
