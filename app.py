from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
import json
import requests
import hashlib
from datetime import datetime, timedelta
import secrets
from werkzeug.utils import secure_filename
import base64
from ai_integration import ai_manager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Production database path for Render
if os.environ.get('RENDER'):
    DATABASE_PATH = '/opt/render/project/src/data/tutor.db'
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
else:
    DATABASE_PATH = 'tutor.db'

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if users table exists and if it needs migration
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = cursor.fetchone() is not None
    
    if table_exists:
        # Check if we need to migrate the existing users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'email' not in columns:
            print("Migrating database schema...")
            
            # Create new users table with authentication fields
            cursor.execute('''
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_guest BOOLEAN DEFAULT FALSE,
                    last_login TIMESTAMP,
                    profile_data TEXT
                )
            ''')
            
            # Copy existing data
            cursor.execute('''
                INSERT INTO users_new (id, username, created_at)
                SELECT id, username, created_at FROM users
            ''')
            
            # Drop old table and rename new one
            cursor.execute('DROP TABLE users')
            cursor.execute('ALTER TABLE users_new RENAME TO users')
            
            print("Database migration completed!")
        else:
            print("Database schema is up to date!")
    else:
        # Create new users table from scratch
        print("Creating new database schema...")
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_guest BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMP,
                profile_data TEXT
            )
        ''')
        print("Users table created!")
    
    # Sessions table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Lessons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            difficulty_level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            lesson_id INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            score INTEGER DEFAULT 0,
            time_spent INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
    ''')
    
    # Quiz results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            lesson_id INTEGER,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            time_taken INTEGER DEFAULT 0,
            answers TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Authentication helper functions
def hash_password(password):
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, stored_hash):
    """Verify a password against its hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

def generate_session_token():
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def create_user_session(user_id, remember_me=False):
    """Create a new user session"""
    session_token = generate_session_token()
    expires_at = datetime.now() + (timedelta(days=30) if remember_me else timedelta(hours=24))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Deactivate old sessions
    cursor.execute('UPDATE user_sessions SET is_active = FALSE WHERE user_id = ?', (user_id,))
    
    # Create new session
    cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, session_token, expires_at))
    
    conn.commit()
    conn.close()
    
    # Set session variables
    session['user_id'] = user_id
    session['session_token'] = session_token
    session.permanent = remember_me
    
    return session_token

def verify_session():
    """Verify current user session"""
    user_id = session.get('user_id')
    session_token = session.get('session_token')
    
    if not user_id or not session_token:
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.*, s.expires_at FROM users u
        JOIN user_sessions s ON u.id = s.user_id
        WHERE u.id = ? AND s.session_token = ? AND s.is_active = TRUE AND s.expires_at > ?
    ''', (user_id, session_token, datetime.now()))
    
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

def login_required(f):
    """Decorator to require authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = verify_session()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Main application page"""
    user = verify_session()
    if not user:
        return render_template('login.html')
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

# Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if len(name) < 2:
            return jsonify({'success': False, 'message': 'Name must be at least 2 characters'}), 400
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'message': 'Valid email is required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Create user
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (name, email, password_hash, datetime.now()))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create session
        create_user_session(user_id)
        
        return jsonify({
            'success': True, 
            'message': 'Account created successfully',
            'user': {'id': user_id, 'username': name, 'email': email}
        })
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'success': False, 'message': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember_me = data.get('remember', False)
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user or not verify_password(password, user['password_hash']):
            conn.close()
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        # Update last login
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user['id']))
        conn.commit()
        conn.close()
        
        # Create session
        create_user_session(user['id'], remember_me)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}
        })
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@app.route('/api/auth/guest', methods=['POST'])
def guest_login():
    """Continue as guest"""
    try:
        guest_name = f"Guest_{secrets.token_hex(4)}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, is_guest, created_at)
            VALUES (?, TRUE, ?)
        ''', (guest_name, datetime.now()))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create session
        create_user_session(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Welcome, guest!',
            'user': {'id': user_id, 'username': guest_name, 'is_guest': True}
        })
        
    except Exception as e:
        print(f"Guest login error: {e}")
        return jsonify({'success': False, 'message': 'Guest login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    try:
        session_token = session.get('session_token')
        
        if session_token:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE user_sessions SET is_active = FALSE WHERE session_token = ?', (session_token,))
            conn.commit()
            conn.close()
        
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
        
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({'success': False, 'message': 'Logout failed'}), 500

@app.route('/api/auth/status')
def auth_status():
    """Check authentication status"""
    user = verify_session()
    if user:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user.get('email'),
                'is_guest': bool(user.get('is_guest', False))
            }
        })
    else:
        return jsonify({'authenticated': False})

@app.route('/api/user/create', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
            user_id = cursor.lastrowid
            conn.commit()
            
            session['user_id'] = user_id
            session['username'] = username
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'username': username
            })
            
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username already exists'}), 400
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lesson/generate', methods=['POST'])
@login_required
def generate_lesson():
    """Generate a new lesson using AI"""
    try:
        data = request.json
        topic = data.get('topic')
        difficulty = data.get('difficulty', 1)
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Generate lesson using AI
        lesson_content = ai_manager.generate_lesson(topic, difficulty)
        
        # Save lesson to database
        user_id = session.get('user_id')
        if user_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO lessons (user_id, topic, content, difficulty_level) VALUES (?, ?, ?, ?)',
                (user_id, topic, lesson_content, difficulty)
            )
            lesson_id = cursor.lastrowid
            conn.commit()
            conn.close()
        else:
            lesson_id = None
        
        return jsonify({
            'success': True,
            'lesson_id': lesson_id,
            'topic': topic,
            'content': lesson_content,
            'difficulty': difficulty
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat interactions with AI"""
    try:
        data = request.json
        message = data.get('message')
        context = data.get('context', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Generate AI response
        ai_response = ai_manager.chat_response(message, context)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/analyze', methods=['POST'])
def analyze_image():
    """Analyze uploaded image using AI"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Analyze image using AI
            analysis = ai_manager.analyze_image(filepath)
            
            # Optionally clean up the uploaded file after analysis
            # os.remove(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'analysis': analysis
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/update', methods=['POST'])
@login_required
def update_progress():
    """Update user progress"""
    try:
        data = request.json
        lesson_id = data.get('lesson_id')
        completed = data.get('completed', False)
        score = data.get('score', 0)
        time_spent = data.get('time_spent', 0)
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if progress record exists
        cursor.execute(
            'SELECT id FROM progress WHERE user_id = ? AND lesson_id = ?',
            (user_id, lesson_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing progress
            cursor.execute('''
                UPDATE progress 
                SET completed = ?, score = ?, time_spent = ?, completed_at = ?
                WHERE user_id = ? AND lesson_id = ?
            ''', (completed, score, time_spent, 
                  datetime.now() if completed else None, user_id, lesson_id))
        else:
            # Create new progress record
            cursor.execute('''
                INSERT INTO progress (user_id, lesson_id, completed, score, time_spent, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, lesson_id, completed, score, time_spent,
                  datetime.now() if completed else None))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/get', methods=['GET'])
@login_required
def get_progress():
    """Get user progress"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT l.topic, l.difficulty_level, p.completed, p.score, p.time_spent, p.completed_at
            FROM lessons l
            LEFT JOIN progress p ON l.id = p.lesson_id AND p.user_id = ?
            WHERE l.user_id = ?
            ORDER BY l.created_at DESC
        ''', (user_id, user_id))
        
        results = cursor.fetchall()
        conn.close()
        
        progress_data = []
        for row in results:
            progress_data.append({
                'topic': row['topic'],
                'difficulty_level': row['difficulty_level'],
                'completed': bool(row['completed']) if row['completed'] is not None else False,
                'score': row['score'] or 0,
                'time_spent': row['time_spent'] or 0,
                'completed_at': row['completed_at']
            })
        
        return jsonify({
            'success': True,
            'progress': progress_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Get AI service status"""
    try:
        available_services = ai_manager.get_available_services()
        primary_service = ai_manager.primary_service.__class__.__name__
        
        return jsonify({
            'success': True,
            'primary_service': primary_service,
            'available_services': available_services,
            'has_ai': len(available_services) > 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/check', methods=['POST'])
def check_quiz_availability():
    """Check if quiz is available for a lesson"""
    try:
        data = request.json
        lesson_id = data.get('lesson_id')
        
        if not lesson_id:
            return jsonify({'error': 'Lesson ID is required'}), 400
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401
        
        # Check if lesson is completed
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT completed FROM progress WHERE user_id = ? AND lesson_id = ?',
            (user_id, lesson_id)
        )
        result = cursor.fetchone()
        conn.close()
        
        quiz_available = result and result['completed']
        
        return jsonify({
            'success': True,
            'quiz_available': bool(quiz_available)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    """Generate quiz questions for a lesson"""
    try:
        data = request.json
        lesson_id = data.get('lesson_id')
        topic = data.get('topic')
        difficulty = data.get('difficulty', 1)
        content = data.get('content', '')
        
        if not lesson_id or not topic:
            return jsonify({'error': 'Lesson ID and topic are required'}), 400
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401
        
        # Generate quiz using AI
        quiz_data = ai_manager.generate_quiz(topic, difficulty, content)
        
        return jsonify({
            'success': True,
            'quiz': quiz_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/save', methods=['POST'])
def save_quiz_results():
    """Save quiz results"""
    try:
        data = request.json
        lesson_id = data.get('lesson_id')
        score = data.get('score')
        total_questions = data.get('total_questions')
        correct_answers = data.get('correct_answers')
        time_taken = data.get('time_taken', 0)
        answers = data.get('answers', [])
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quiz_results (user_id, lesson_id, score, total_questions, correct_answers, time_taken, answers)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, lesson_id, score, total_questions, correct_answers, time_taken, json.dumps(answers)))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/diagram/generate', methods=['POST'])
def generate_diagram():
    """Generate ASCII diagram for a concept"""
    try:
        data = request.get_json()
        
        if not data or 'concept' not in data:
            return jsonify({'error': 'Concept is required'}), 400
        
        concept = data['concept']
        diagram_type = data.get('type', 'flowchart')
        
        # Generate diagram using AI
        diagram = ai_manager.generate_diagram(concept, diagram_type)
        
        return jsonify({
            'success': True,
            'diagram': diagram,
            'concept': concept,
            'type': diagram_type
        })
        
    except Exception as e:
        print(f"Error generating diagram: {e}")
        return jsonify({'error': 'Failed to generate diagram'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)