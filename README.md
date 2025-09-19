# AI Personal Tutor Web Application

A multimodal personal tutor that combines text, voice, and image capabilities to create interactive and adaptive learning experiences.

## Features

- **Text-based Lessons**: AI-generated personalized lessons on any topic
- **Voice Integration**: Text-to-speech for lesson narration and speech-to-text for voice input
- **Image Analysis**: Upload and analyze images related to your learning topic
- **Adaptive Learning**: Tracks progress and adjusts content difficulty
- **Progress Tracking**: Monitor your learning journey with detailed statistics
- **Chat Interface**: Interactive AI tutor for questions and discussions

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python Flask
- **Database**: SQLite (file-based, no setup required)
- **AI Integration**: Ready for integration with OpenAI, Hugging Face, or Google Gemini APIs
- **Voice**: Web Speech API (built into modern browsers)
- **Deployment**: Render-ready configuration

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Modern web browser with speech recognition support

### Local Development

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser and navigate to `http://localhost:5000`

### Environment Variables

For AI integration, set these environment variables:

```bash
# OpenAI API (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key

# Hugging Face API (if using Hugging Face)
HUGGINGFACE_API_KEY=your_huggingface_api_key

# Google Gemini API (if using Google)
GOOGLE_API_KEY=your_google_api_key
```

## Deployment on Render

1. Fork this repository to your GitHub account
2. Connect your GitHub account to Render
3. Create a new Web Service on Render
4. Select this repository
5. Configure the deployment:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Add your API keys as needed
6. Deploy!

The application will be available at your Render URL.

## 🤖 **AI Integration - CONFIGURED & READY!**

Your application is now **fully configured** with **OpenRouter** using the **Meta Llama 3.3 8B Instruct (FREE)** model!

### **✅ Current Setup:**
- **API Service**: OpenRouter (https://openrouter.ai)
- **Model**: Meta Llama 3.3 70B Instruct (Free tier)
- **API Key**: Pre-configured and working
- **Status**: 🟢 **ACTIVE & READY TO USE**

### **🚀 Capabilities:**
- 📚 **Smart Lesson Generation**: Creates comprehensive, structured lessons on any topic
- 💬 **Interactive AI Chat**: Answers questions with educational context and lesson awareness
- 🖼️ **Image Analysis**: Provides educational insights about uploaded images
- 🎯 **Adaptive Content**: Adjusts difficulty and explanations based on user level
- 🧠 **Context-Aware**: Remembers current lesson content for relevant responses

### **💰 Free Usage:**
The Meta Llama 3.3 8B model on OpenRouter is **completely free** with generous limits - perfect for educational use!

### **🔧 No Setup Required:**
Everything is configured and ready to use. Just run the application and start learning!

## File Structure

```
AI Tutor Web App/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── templates/
│   └── index.html        # Main HTML template
└── uploads/              # Image upload directory
```

## Features in Detail

### Lesson Generation
- Enter any topic and difficulty level
- AI generates structured, personalized content
- Text-to-speech narration with speed control
- Progress tracking and completion marking

### Interactive Chat
- Ask questions about your lesson
- Voice input support
- Context-aware AI responses
- Real-time conversation

### Image Analysis
- Drag-and-drop or click to upload images
- AI analyzes visual content
- Relates images to learning objectives
- Provides educational insights

### Progress Tracking
- Lesson completion statistics
- Time spent learning
- Average scores
- Learning history

## Browser Compatibility

- **Chrome**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support

Voice features require HTTPS in production (automatically handled by Render).

## Contributing

This is a free, open-source educational project. Feel free to:
- Add new features
- Improve the UI/UX
- Integrate additional AI services
- Enhance the learning algorithms

## Database Schema

The application uses SQLite with three main tables:
- `users`: User accounts and profiles
- `lessons`: Generated lesson content
- `progress`: Learning progress and statistics

## Security Notes

- File uploads are validated and secured
- Image files are limited to 16MB
- SQL injection protection through parameterized queries
- Session management for user authentication

## Future Enhancements

- Multiple language support
- Advanced progress analytics
- Collaborative learning features
- Mobile app development
- Additional AI model integrations

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please check the documentation or create an issue in the repository.