from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from colorize import colorize_image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get('file')
        if not file or file.filename == '':
            return "No selected file", 400
        
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            output_filename = 'colorized_' + filename
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            colorize_image(file_path, output_path)  # Ensure this function correctly processes and saves the image
            
            return redirect(url_for('display_image', filename=output_filename))
        else:
            return "File not allowed", 400
    return render_template('index.html')

@app.route('/uploads/<filename>')
def display_image(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return "File not found", 404

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
