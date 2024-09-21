from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import io
import os, time
import steganography

app = Flask(__name__)

ENCODED_IMAGE_FOLDER = 'encoded-image'
UPLOAD_FOLDER = 'uploads'
app.config['ENCODED_IMAGE_FOLDER'] = ENCODED_IMAGE_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/test")
def test():
    return steganography.test()
    
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/encode", methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        image = request.files['image']
        message = request.form['message']
        password = request.form['password']

        # new_image_name = "new_"+str(time.time())+"_"+image.filename
        # upload_image_path = os.path.join(app.config['UPLOAD_FOLDER'], new_image_name)
        # image.save(upload_image_path)

        # encoded_image = steganography.encodeMessageToImage(upload_image_path, message, password)
        # image_path = os.path.join(app.config['ENCODED_IMAGE_FOLDER'], new_image_name)
        # encoded_image.save(image_path)

        filename, file_extension = os.path.splitext(image.filename)
        file_extension = file_extension.lower()

        encoded_image = steganography.encodeMessageToImage(image, message, password)

        img_io = io.BytesIO()

        format_map = {
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.png': 'PNG',
            '.gif': 'GIF',
            '.bmp': 'BMP',
            '.tiff': 'TIFF'
        }
        img_format = format_map.get(file_extension)
        encoded_image.save(img_io, format=img_format)
        img_io.seek(0)      

        return send_file(img_io, as_attachment=True, download_name='encoded_'+image.filename)
    else:
        return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        image = request.files['image']
        password = request.form['password']

        decoded_message = steganography.decodeImageToMessage(image, password)
        return decoded_message
    else:
        return render_template('decode.html')



if __name__ == '__main__':
    app.run(debug=True, port=5000)