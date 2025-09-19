#!/usr/bin/env python3
"""
Setup script for AI Personal Tutor
Helps configure the application for deployment
"""

import os
import shutil
import secrets

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file from template")
            print("📝 Please edit .env file to add your AI API keys")
        else:
            with open('.env', 'w') as f:
                f.write(f'SECRET_KEY={secrets.token_hex(32)}\n')
                f.write('PORT=5000\n')
            print("✓ Created basic .env file")
    else:
        print("✓ .env file already exists")

def check_requirements():
    """Check if requirements are satisfied"""
    try:
        import flask
        import flask_cors
        import requests
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'static/css', 'static/js', 'templates']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")

def setup_database():
    """Initialize the database"""
    try:
        from app import init_db
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

def print_ai_setup_instructions():
    """Print AI setup instructions"""
    print("\n" + "="*60)
    print("🤖 AI INTEGRATION SETUP")
    print("="*60)
    print("To enable AI features, you need to set up at least one AI service:")
    print()
    print("1. 🌟 Google Gemini (Recommended - Most generous free tier)")
    print("   • Visit: https://makersuite.google.com/app/apikey")
    print("   • Get your API key")
    print("   • Add to .env: GOOGLE_API_KEY=your_key_here")
    print()
    print("2. 🧠 OpenAI (Good quality)")
    print("   • Visit: https://platform.openai.com/api-keys")
    print("   • Get $5 free credits for new accounts")
    print("   • Add to .env: OPENAI_API_KEY=your_key_here")
    print()
    print("3. 🤗 Hugging Face (Free with rate limits)")
    print("   • Visit: https://huggingface.co/settings/tokens")
    print("   • Create a token")
    print("   • Add to .env: HUGGINGFACE_API_KEY=your_key_here")
    print()
    print("💡 The app will work with fallback responses even without AI keys!")
    print("="*60)

def print_deployment_instructions():
    """Print deployment instructions"""
    print("\n" + "="*60)
    print("🚀 DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    print("For Render.com (Free):")
    print("1. Push your code to GitHub")
    print("2. Connect GitHub to Render")
    print("3. Create new Web Service")
    print("4. Build Command: pip install -r requirements.txt")
    print("5. Start Command: gunicorn app:app")
    print("6. Add environment variables in Render dashboard")
    print()
    print("For local development:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5000")
    print("="*60)

def main():
    """Main setup function"""
    print("🎓 AI Personal Tutor - Setup Script")
    print("=" * 40)
    
    # Create environment file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Check requirements
    if not check_requirements():
        return
    
    # Setup database
    setup_database()
    
    print("\n✅ Setup completed successfully!")
    
    # Print additional instructions
    print_ai_setup_instructions()
    print_deployment_instructions()
    
    print("\n🎉 Your AI Personal Tutor is ready!")
    print("Run 'python app.py' to start the application")

if __name__ == "__main__":
    main()