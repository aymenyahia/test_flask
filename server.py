from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.secret_key = 'super_secret_key'  # Needed for flash messages

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Image uploaded successfully!')
            return redirect(url_for('upload_file'))
        else:
            flash('File type not allowed. Only images are permitted.')
            return redirect(request.url)
    
    # HTML form
    html = '''
    <!doctype html>
    <html>
    <head>
        <title>Image Upload Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            form { margin: 20px 0; }
            input[type=file] { margin: 10px 0; }
            .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>Upload an Image</h1>
        
        {% for message in get_flashed_messages() %}
            <div class="message {% if 'success' in message.lower() %}success{% else %}error{% endif %}">
                {{ message }}
            </div>
        {% endfor %}
        
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*">
            <br><br>
            <input type="submit" value="Upload Image">
        </form>
        
        <h2>Uploaded Images</h2>
        <ul>
        {% for file in uploaded_files %}
            <li><a href="/uploads/{{ file }}" target="_blank">{{ file }}</a></li>
        {% endfor %}
        </ul>
    </body>
    </html>
    '''
    
    uploaded_files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    return render_template_string(html, uploaded_files=uploaded_files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("Server starting at https://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'), cert_reqs='CERT_REQUIRED', ca_certs='ca.crt')
