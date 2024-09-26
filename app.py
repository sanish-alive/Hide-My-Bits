from flask import Flask, render_template, request, send_file
import io, os
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
        text_file = request.files['text-file']
        password = request.form['password']

        message = text_file.read().decode('utf-8')

        encoded_image = steganography.encodeMessageToImage(image, message, password)

        img_io = io.BytesIO()

        encoded_image.save(img_io, format='PNG')
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

        text_file_io = io.BytesIO()
        text_file_io.write(decoded_message.encode('utf-8'))
        text_file_io.seek(0)

        return send_file(text_file_io, as_attachment=True, download_name='decoded_text.txt', mimetype='text/plain')
        return decoded_message
    else:
        return render_template('decode.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)