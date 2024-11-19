from flask import Flask, render_template, request, send_file, url_for, redirect, after_this_request
import tempfile, os
from steganography import Steganography

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

@app.route('/hide-my-bits')
def hideMyBits():
    return redirect(url_for('home'))

@app.route("/encode", methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        image = request.files['image']
        text_file = request.files['text-file']
        password = request.form['password']

        message = text_file.read().decode('utf-8')

        sg = Steganography(password)
        encoded_image = sg.encode_message_to_image(image, message)

        # Create a temporary file
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        try:
            encoded_image.save(tmp_file.name, format='PNG')
            tmp_file_path = tmp_file.name
        finally:
            tmp_file.close()

        @after_this_request
        def cleanup(response):
            try:
                os.remove(tmp_file_path)
            except Exception as e:
                app.logger.error(f"Error deleting file: {e}")
            return response

        return send_file(tmp_file_path, as_attachment=True, download_name='encoded_' + image.filename)
    else:
        return render_template('encode.html')



@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        image = request.files['image']
        password = request.form['password']

        sg = Steganography(password)
        decoded_message = sg.decode_image_to_message(image)

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8')
        try:
            tmp_file.write(decoded_message)
            tmp_file_path = tmp_file.name
        finally:
            tmp_file.close()

        @after_this_request
        def cleanup(response):
            try:
                os.remove(tmp_file_path)
            except Exception as e:
                app.logger.error(f"Error deleting file: {e}")
            return response

        return send_file(tmp_file_path, as_attachment=True, download_name='decoded_text.txt', mimetype='text/plain')
    else:
        return render_template('decode.html')

application = app
if __name__ == '__main__':
    app.run(debug=True, port=5000)