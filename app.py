from flask import Flask,render_template, request, flash
import pytesseract
import PIL.Image
import cv2
import os
from werkzeug.utils import secure_filename
import base64

UPLOAD_FOLDER = './samples'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "12sad2d"

@app.route('/', methods=['GET', 'POST'])
def index():
    str_tesseract = ""  # Set a default value for str_tesseract
    img_box_base64 = None

    if request.method == 'POST':
        #Get image from user
        img = request.files['imageFile']

        if img:
            #if the image uploaded successfully secure it and save it to samples folder
            imgName = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], imgName))
            
            #Apply tesseract on the image
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], imgName)
            str_tesseract = pytesseract.image_to_string(PIL.Image.open(img_path))

            if not str_tesseract:
                flash("Tesseract could not recognize text", "error")
            #Generate box image
            img_box = cv2.imread(img_path)
            height, width, _ = img_box.shape

            #Get the boundaries for each letter
            boxes = pytesseract.image_to_boxes(img_box)
            for box in boxes.splitlines():
                box = box.split(" ")
                img_box = cv2.rectangle(img_box, (int(box[1]), height - int(box[2])), (int(box[3]), height - int(box[4])), (0, 255, 0), 2)

             # Encode img_box to base64 for HTML rendering
            _, buffer = cv2.imencode('.png', img_box)
            img_box_base64 = base64.b64encode(buffer).decode('utf-8')
        else:
            flash("Image uploading unsuccessful", "error")
            #render the same html page and display the result of the tesseract
        return render_template('form.html', str_tesseract=str_tesseract, img_box_base64=img_box_base64)
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
