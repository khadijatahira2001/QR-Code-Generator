from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import qrcode
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['QR_FOLDER'] = 'static/qrcodes'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['QR_FOLDER']):
    os.makedirs(app.config['QR_FOLDER'])

def generate_qr_code(data, qr_code_filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    filepath = os.path.join(app.config['QR_FOLDER'], qr_code_filename)
    img.save(filepath)
    return qr_code_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form.get('option')
        if option == 'text':
            data = request.form.get('data')
            if data:
                qr_code_filename = f"{uuid.uuid4()}.png"
                qr_code = generate_qr_code(data, qr_code_filename)
                return render_template('index.html', qr_code=qr_code)
        elif option in ['image', 'pdf']:
            file = request.files.get(option)
            if file and file.filename:
                filename = f"{uuid.uuid4()}_{file.filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                qr_code_filename = f"{uuid.uuid4()}.png"
                qr_code = generate_qr_code(url_for('uploaded_file', filename=filename, _external=True), qr_code_filename)
                return render_template('index.html', qr_code=qr_code)
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/qrcodes/<filename>')
def qrcode_file(filename):
    return send_from_directory(app.config['QR_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
