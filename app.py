from flask import Flask,render_template, request
import pytesseract
import PIL.Image
import cv2
import os
from werkzeug.utils import secure_filename
import base64

UPLOAD_FOLDER = './samples'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
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

"""
import pytesseract
import PIL.Image
import cv2

Page segmentation modes:
  0    Orientation and script detection (OSD) only.
  1    Automatic page segmentation with OSD.
  2    Automatic page segmentation, but no OSD, or OCR. (not implemented)
  3    Fully automatic page segmentation, but no OSD. (Default)
  4    Assume a single column of text of variable sizes.
  5    Assume a single uniform block of vertically aligned text.
  6    Assume a single uniform block of text.
  7    Treat the image as a single text line.
  8    Treat the image as a single word.
  9    Treat the image as a single word in a circle.
 10    Treat the image as a single character.
 11    Sparse text. Find as much text as possible in no particular order.
 12    Sparse text with OSD.
 13    Raw line. Treat the image as a single text line,
       bypassing hacks that are Tesseract-specific.

OCR Engine modes:
  0    Legacy engine only.
  1    Neural nets LSTM engine only.
  2    Legacy + LSTM engines.
  3    Default, based on what is available.

myconfig = r"--psm 3 --oem 3"

img = cv2.imread("samples\sample1.jpg")
height, width, _ = img.shape
boxes = pytesseract.image_to_boxes(img, config=myconfig)

for box in boxes.splitlines():
    box = box.split(" ")
    img = cv2.rectangle(img, (int(box[1]), height - int(box[2])), (int(box[3]), height - int(box[4])), (0, 255, 0), 2)

cv2.imshow("img", img)
cv2.waitKey(0)    
print(pytesseract.image_to_string(img, config=myconfig))

"""