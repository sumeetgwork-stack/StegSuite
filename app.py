import os
import secrets
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, render_template, send_file, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from models import db, User

from utils.image_stego import encode_image, decode_image
from utils.audio_stego import encode_audio, decode_audio
from utils.video_stego import encode_video, decode_video
from utils.text_stego import (
    encode_text_zwsp, decode_text_zwsp,
    encode_text_whitespace, decode_text_whitespace,
    encode_text_formatting, decode_text_formatting
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-change-in-prod')
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///stegsuite.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- OAuth Setup ---
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID', 'DUMMY_ID_TO_PREVENT_CRASH'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'DUMMY_SECRET_TO_PREVENT_CRASH'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'bmp'}
ALLOWED_AUDIO = {'wav'}
ALLOWED_VIDEO = {'mp4', 'avi', 'mov'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Create DB tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# -------- AUTH ROUTES --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email address already exists', 'error')
            return redirect(url_for('signup'))
            
        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('index'))
        
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/auth/google')
def auth_google():
    redirect_uri = url_for('auth_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def auth_google_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    if not user_info:
        flash('Google authentication failed', 'error')
        return redirect(url_for('login'))
        
    email = user_info['email']
    name = user_info.get('name')
    google_id = user_info['sub']
    
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name, google_id=google_id)
        db.session.add(user)
        db.session.commit()
    elif not user.google_id:
        user.google_id = google_id
        db.session.commit()
        
    login_user(user)
    return redirect(url_for('index'))

# -------- STEGO PAGE ROUTES --------
@app.route('/stego/<type>')
@login_required
def stego_page(type):
    if type not in ['image', 'audio', 'video', 'text']:
        return redirect(url_for('index'))
    mode = request.args.get('mode', 'encode')
    return render_template('stego.html', type=type, mode=mode)

# -------- IMAGE ROUTES --------
@app.route('/encode/image', methods=['POST'])
@login_required
def encode_image_route():
    if 'image' not in request.files or 'message' not in request.form:
        return jsonify({'error': 'Missing file or message'}), 400
    
    file = request.files['image']
    message = request.form['message']
    
    if not allowed_file(file.filename, ALLOWED_IMAGE):
        return jsonify({'error': 'Invalid image format. Use PNG, JPG, JPEG, BMP'}), 400
    
    filename = secure_filename(file.filename)
    filename_no_ext = filename.rsplit('.', 1)[0]
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    output_filename = f"stego_img_{secrets.token_hex(4)}_{filename_no_ext}.png"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    try:
        encode_image(input_path, message, output_path)
        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}',
            'type': 'image'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decode/image', methods=['POST'])
@login_required
def decode_image_route():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['image']
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
    file.save(input_path)
    
    try:
        message = decode_image(input_path)
        os.remove(input_path)
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------- AUDIO ROUTES --------
@app.route('/encode/audio', methods=['POST'])
@login_required
def encode_audio_route():
    if 'audio' not in request.files or 'message' not in request.form:
        return jsonify({'error': 'Missing file or message'}), 400
    
    file = request.files['audio']
    message = request.form['message']
    
    if not allowed_file(file.filename, ALLOWED_AUDIO):
        return jsonify({'error': 'Invalid audio format. Use WAV only'}), 400
    
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    output_filename = f"stego_aud_{secrets.token_hex(4)}_{filename}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    try:
        encode_audio(input_path, message, output_path)
        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}',
            'type': 'audio'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decode/audio', methods=['POST'])
@login_required
def decode_audio_route():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['audio']
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
    file.save(input_path)
    
    try:
        message = decode_audio(input_path)
        os.remove(input_path)
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------- VIDEO ROUTES --------
@app.route('/encode/video', methods=['POST'])
@login_required
def encode_video_route():
    if 'video' not in request.files or 'message' not in request.form:
        return jsonify({'error': 'Missing file or message'}), 400
    
    file = request.files['video']
    message = request.form['message']
    
    if not allowed_file(file.filename, ALLOWED_VIDEO):
        return jsonify({'error': 'Invalid video format. Use MP4, AVI, MOV'}), 400
    
    filename = secure_filename(file.filename)
    filename_no_ext = filename.rsplit('.', 1)[0]
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    output_filename = f"stego_vid_{secrets.token_hex(4)}_{filename_no_ext}.avi"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    try:
        encode_video(input_path, message, output_path)
        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}',
            'type': 'video'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decode/video', methods=['POST'])
@login_required
def decode_video_route():
    if 'video' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['video']
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
    file.save(input_path)
    
    try:
        message = decode_video(input_path)
        os.remove(input_path)
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------- TEXT ROUTES --------
@app.route('/encode/text', methods=['POST'])
@login_required
def encode_text_route():
    data = request.get_json(silent=True) or request.form
    cover_text = data.get('cover_text', '')
    secret_message = data.get('message', '')
    method = data.get('method', 'zwsp')
    
    if not cover_text or not secret_message:
        return jsonify({'error': 'Missing cover text or secret message'}), 400
    
    try:
        if method == 'zwsp':
            result = encode_text_zwsp(cover_text, secret_message)
        elif method == 'whitespace':
            result = encode_text_whitespace(cover_text, secret_message)
        elif method == 'formatting':
            result = encode_text_formatting(cover_text, secret_message)
        else:
            return jsonify({'error': 'Invalid method'}), 400
        
        return jsonify({'success': True, 'stego_text': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decode/text', methods=['POST'])
@login_required
def decode_text_route():
    data = request.get_json(silent=True) or request.form
    stego_text = data.get('stego_text', '')
    method = data.get('method', 'zwsp')
    
    if not stego_text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        if method == 'zwsp':
            result = decode_text_zwsp(stego_text)
        elif method == 'whitespace':
            result = decode_text_whitespace(stego_text)
        elif method == 'formatting':
            result = decode_text_formatting(stego_text)
        else:
            return jsonify({'error': 'Invalid method'}), 400
        
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------- DOWNLOAD --------
@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], filename),
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
