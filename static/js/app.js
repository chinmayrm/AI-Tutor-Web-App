// Global Variables
let currentUser = null;
let currentLesson = null;
let currentQuiz = null;
let quizStartTime = null;
let speechSynthesis = window.speechSynthesis;
let speechRecognition = null;
let isListening = false;
let currentUtterance = null;
let lessonStartTime = null;

// Initialize Speech Recognition
if ('webkitSpeechRecognition' in window) {
    speechRecognition = new webkitSpeechRecognition();
    speechRecognition.continuous = false;
    speechRecognition.interimResults = false;
    speechRecognition.lang = 'en-US';
} else if ('SpeechRecognition' in window) {
    speechRecognition = new SpeechRecognition();
    speechRecognition.continuous = false;
    speechRecognition.interimResults = false;
    speechRecognition.lang = 'en-US';
}

// DOM Elements
const userModal = document.getElementById('userModal');
const mainInterface = document.getElementById('mainInterface');
const usernameInput = document.getElementById('usernameInput');
const createUserBtn = document.getElementById('createUserBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');

// Tab Elements
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Lesson Elements
const topicInput = document.getElementById('topicInput');
const difficultySelect = document.getElementById('difficultySelect');
const generateLessonBtn = document.getElementById('generateLessonBtn');
const lessonContent = document.getElementById('lessonContent');
const lessonText = document.getElementById('lessonText');
const readAloudBtn = document.getElementById('readAloudBtn');
const stopReadingBtn = document.getElementById('stopReadingBtn');
const pauseReadingBtn = document.getElementById('pauseReadingBtn');
const speedSlider = document.getElementById('speedSlider');
const speedValue = document.getElementById('speedValue');
const markCompleteBtn = document.getElementById('markCompleteBtn');
const askQuestionBtn = document.getElementById('askQuestionBtn');

// Chat Elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');
const voiceInputBtn = document.getElementById('voiceInputBtn');
const voiceStatus = document.getElementById('voiceStatus');

// Image Elements
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const selectImageBtn = document.getElementById('selectImageBtn');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const analyzeImageBtn = document.getElementById('analyzeImageBtn');
const imageAnalysis = document.getElementById('imageAnalysis');
const analysisContent = document.getElementById('analysisContent');

// Progress Elements
const lessonsCompleted = document.getElementById('lessonsCompleted');
const totalStudyTime = document.getElementById('totalStudyTime');
const averageScore = document.getElementById('averageScore');
const progressHistory = document.getElementById('progressHistory');

// Quiz Elements
const quizNotAvailable = document.getElementById('quizNotAvailable');
const quizAvailable = document.getElementById('quizAvailable');
const quizTopic = document.getElementById('quizTopic');
const quizDifficulty = document.getElementById('quizDifficulty');
const currentQuestion = document.getElementById('currentQuestion');
const totalQuestions = document.getElementById('totalQuestions');
const questionText = document.getElementById('questionText');
const questionOptions = document.getElementById('questionOptions');
const submitAnswerBtn = document.getElementById('submitAnswerBtn');
const nextQuestionBtn = document.getElementById('nextQuestionBtn');
const quizResult = document.getElementById('quizResult');
const finalScore = document.getElementById('finalScore');
const finalPercentage = document.getElementById('finalPercentage');
const quizTime = document.getElementById('quizTime');
const quizFeedback = document.getElementById('quizFeedback');
const retakeQuizBtn = document.getElementById('retakeQuizBtn');

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// User Management Events
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
}

// Tab Navigation
tabBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        const tabName = this.dataset.tab;
        switchTab(tabName);
        
        // Load progress when switching to progress tab
        if (tabName === 'progress') {
            loadProgress();
        }
        
        // Load quiz when switching to quiz tab
        if (tabName === 'quiz') {
            checkQuizAvailability();
        }
    });
});

// Lesson Management
generateLessonBtn.addEventListener('click', generateLesson);
topicInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        generateLesson();
    }
});

// Reading Controls
readAloudBtn.addEventListener('click', startReading);
stopReadingBtn.addEventListener('click', stopReading);
pauseReadingBtn.addEventListener('click', pauseReading);
speedSlider.addEventListener('input', updateReadingSpeed);
markCompleteBtn.addEventListener('click', markLessonComplete);
askQuestionBtn.addEventListener('click', function() {
    switchTab('chat');
    chatInput.focus();
});

// Quiz
submitAnswerBtn.addEventListener('click', submitQuizAnswer);
nextQuestionBtn.addEventListener('click', nextQuizQuestion);
retakeQuizBtn.addEventListener('click', startQuiz);

// Chat
sendChatBtn.addEventListener('click', sendChatMessage);
chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
});

// Voice Input
if (speechRecognition) {
    voiceInputBtn.addEventListener('click', toggleVoiceInput);
    
    speechRecognition.onstart = function() {
        isListening = true;
        voiceInputBtn.classList.add('recording');
        voiceStatus.textContent = 'Listening...';
    };
    
    speechRecognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        isListening = false;
        voiceInputBtn.classList.remove('recording');
        voiceStatus.textContent = '';
        
        // Automatically send the message
        setTimeout(() => {
            sendChatMessage();
        }, 500);
    };
    
    speechRecognition.onerror = function(event) {
        isListening = false;
        voiceInputBtn.classList.remove('recording');
        voiceStatus.textContent = 'Error occurred';
        showToast('Voice recognition error: ' + event.error, 'error');
        
        setTimeout(() => {
            voiceStatus.textContent = '';
        }, 3000);
    };
    
    speechRecognition.onend = function() {
        isListening = false;
        voiceInputBtn.classList.remove('recording');
        voiceStatus.textContent = '';
    };
} else {
    voiceInputBtn.style.display = 'none';
    showToast('Voice recognition not supported in this browser', 'warning');
}

// Image Upload
selectImageBtn.addEventListener('click', () => imageInput.click());
imageInput.addEventListener('change', handleImageSelect);
analyzeImageBtn.addEventListener('click', analyzeImage);

// Drag and Drop
uploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', function(e) {
    e.preventDefault();
    this.classList.remove('dragover');
});

uploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleImageFile(files[0]);
    }
});

uploadArea.addEventListener('click', () => imageInput.click());

// Functions
async function initializeApp() {
    // Check authentication status
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.user;
            const welcomeText = document.getElementById('welcomeText');
            if (welcomeText) {
                welcomeText.textContent = `Welcome, ${currentUser.username}!`;
            }
            loadProgress();
            
            // Initialize diagram controls if available
            if (typeof initializeDiagramControls === 'function') {
                initializeDiagramControls();
            }
        } else {
            // Redirect to login if not authenticated
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/login';
    }
}

async function handleLogout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST'
        });
        
        if (response.ok) {
            window.location.href = '/login';
        } else {
            showToast('Logout failed', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showToast('Logout failed', 'error');
    }
}

function switchTab(tabName) {
    // Update tab buttons
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    tabContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === tabName + 'Tab') {
            content.classList.add('active');
        }
    });
}

function generateLesson() {
    const topic = topicInput.value.trim();
    const difficulty = difficultySelect.value;
    
    if (!topic) {
        showToast('Please enter a topic to learn about', 'error');
        return;
    }
    
    showLoading('Generating your personalized lesson...');
    lessonStartTime = Date.now();
    
    fetch('/api/lesson/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            topic: topic, 
            difficulty: parseInt(difficulty) 
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            currentLesson = data;
            displayLesson(data);
            showToast('Lesson generated successfully!', 'success');
        } else {
            showToast(data.error || 'Failed to generate lesson', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showToast('Network error. Please try again.', 'error');
    });
}

function displayLesson(lesson) {
    // Convert markdown-like content to HTML
    let htmlContent = lesson.content
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^\*\*(.*?)\*\*/gm, '<strong>$1</strong>')
        .replace(/^\* (.*$)/gm, '<li>$1</li>')
        .replace(/^(\d+\.) (.*$)/gm, '<li>$1 $2</li>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/^(?!<[h|l|s])/gm, '<p>')
        .replace(/$(?![h|l|s])/gm, '</p>')
        .replace(/<li>/g, '<ul><li>')
        .replace(/<\/li>(?!\s*<li>)/g, '</li></ul>');
    
    // Clean up any malformed HTML
    htmlContent = htmlContent.replace(/<\/ul>\s*<ul>/g, '');
    
    lessonText.innerHTML = htmlContent;
    lessonContent.classList.remove('hidden');
    
    // Scroll to lesson content
    lessonContent.scrollIntoView({ behavior: 'smooth' });
}

function startReading() {
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
    }
    
    const text = lessonText.textContent;
    if (!text) {
        showToast('No lesson content to read', 'error');
        return;
    }
    
    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.rate = parseFloat(speedSlider.value);
    currentUtterance.pitch = 1;
    currentUtterance.volume = 1;
    
    currentUtterance.onstart = function() {
        readAloudBtn.classList.add('hidden');
        stopReadingBtn.classList.remove('hidden');
        pauseReadingBtn.classList.remove('hidden');
    };
    
    currentUtterance.onend = function() {
        readAloudBtn.classList.remove('hidden');
        stopReadingBtn.classList.add('hidden');
        pauseReadingBtn.classList.add('hidden');
    };
    
    speechSynthesis.speak(currentUtterance);
}

function stopReading() {
    speechSynthesis.cancel();
    readAloudBtn.classList.remove('hidden');
    stopReadingBtn.classList.add('hidden');
    pauseReadingBtn.classList.add('hidden');
}

function pauseReading() {
    if (speechSynthesis.speaking && !speechSynthesis.paused) {
        speechSynthesis.pause();
        pauseReadingBtn.innerHTML = '<i class="fas fa-play"></i> Resume';
    } else {
        speechSynthesis.resume();
        pauseReadingBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
    }
}

function updateReadingSpeed() {
    const speed = speedSlider.value;
    speedValue.textContent = speed + 'x';
    
    if (currentUtterance && speechSynthesis.speaking) {
        // Stop current speech and restart with new speed
        speechSynthesis.cancel();
        setTimeout(() => {
            startReading();
        }, 100);
    }
}

function markLessonComplete() {
    if (!currentLesson) {
        showToast('No active lesson to complete', 'error');
        return;
    }
    
    const timeSpent = lessonStartTime ? Math.floor((Date.now() - lessonStartTime) / 1000 / 60) : 0;
    
    fetch('/api/progress/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            lesson_id: currentLesson.lesson_id,
            completed: true,
            score: 100, // Default score for completed lesson
            time_spent: timeSpent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Lesson marked as complete! Great job!', 'success');
            markCompleteBtn.innerHTML = '<i class="fas fa-check"></i> Completed';
            markCompleteBtn.disabled = true;
            
            // Show quiz notification and enable quiz tab
            showToast('Quiz unlocked! Check the Quiz tab to test your knowledge.', 'info');
            setTimeout(() => {
                const quizTab = document.querySelector('[data-tab="quiz"]');
                quizTab.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                quizTab.style.color = 'white';
                setTimeout(() => {
                    quizTab.style.background = '';
                    quizTab.style.color = '';
                }, 3000);
            }, 1000);
        } else {
            showToast(data.error || 'Failed to update progress', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Network error. Please try again.', 'error');
    });
}

// Diagram Generation Functions
function initializeDiagramControls() {
    const generateBtn = document.getElementById('generateDiagramBtn');
    
    if (generateBtn) {
        generateBtn.addEventListener('click', generateDiagram);
    }
}

async function generateDiagram() {
    if (!currentLesson || !currentLesson.topic) {
        showToast('Please generate a lesson first', 'error');
        return;
    }
    
    const diagramType = document.getElementById('diagramType').value;
    const generateBtn = document.getElementById('generateDiagramBtn');
    
    // Show loading state
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    
    try {
        const response = await fetch('/api/diagram/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                concept: currentLesson.topic,
                type: diagramType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayDiagram(data.diagram, data.concept, data.type);
            showToast('Diagram generated successfully!', 'success');
        } else {
            showToast(data.error || 'Failed to generate diagram', 'error');
        }
    } catch (error) {
        console.error('Error generating diagram:', error);
        showToast('Failed to generate diagram', 'error');
    } finally {
        // Reset button state
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-chart-bar"></i> Generate Diagram';
    }
}

function displayDiagram(diagram, concept, type) {
    const lessonText = document.getElementById('lessonText');
    
    // Create diagram container
    const diagramContainer = document.createElement('div');
    diagramContainer.className = 'diagram-container';
    diagramContainer.innerHTML = `
        <div class="visual-note">
            <h3>📊 Visual Diagram: ${concept} (${type})</h3>
            <pre class="diagram-content">${diagram}</pre>
            <button class="btn-secondary" onclick="copyDiagram('${diagram.replace(/'/g, "\\'")}')">
                <i class="fas fa-copy"></i> Copy Diagram
            </button>
        </div>
        <hr>
    `;
    
    // Add to the beginning of lesson content
    lessonText.insertBefore(diagramContainer, lessonText.firstChild);
}

function copyDiagram(diagram) {
    navigator.clipboard.writeText(diagram).then(() => {
        showToast('Diagram copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy diagram', 'error');
    });
}

function sendChatMessage() {
    const message = chatInput.value.trim();
    
    if (!message) {
        showToast('Please enter a message', 'error');
        return;
    }
    
    // Add user message to chat
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    // Show typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message ai typing';
    typingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AI is thinking...';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Send message to AI
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            message: message,
            context: currentLesson ? currentLesson.content : ''
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove typing indicator
        chatMessages.removeChild(typingDiv);
        
        if (data.success) {
            addChatMessage(data.response, 'ai');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'ai');
        }
    })
    .catch(error => {
        // Remove typing indicator
        if (chatMessages.contains(typingDiv)) {
            chatMessages.removeChild(typingDiv);
        }
        console.error('Error:', error);
        addChatMessage('Sorry, I encountered a network error. Please try again.', 'ai');
    });
}

function addChatMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const timestamp = new Date().toLocaleTimeString();
    messageDiv.innerHTML = `
        <div>${message}</div>
        <div class="timestamp">${timestamp}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function toggleVoiceInput() {
    if (!speechRecognition) {
        showToast('Voice recognition not supported', 'error');
        return;
    }
    
    if (isListening) {
        speechRecognition.stop();
    } else {
        speechRecognition.start();
    }
}

function handleImageSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleImageFile(file);
    }
}

function handleImageFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Please select a valid image file', 'error');
        return;
    }
    
    if (file.size > 16 * 1024 * 1024) {
        showToast('Image file is too large. Please select a file under 16MB.', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImg.src = e.target.result;
        imagePreview.classList.remove('hidden');
        imageAnalysis.classList.add('hidden');
    };
    reader.readAsDataURL(file);
}

function analyzeImage() {
    const file = imageInput.files[0];
    if (!file) {
        showToast('Please select an image first', 'error');
        return;
    }
    
    showLoading('Analyzing image...');
    
    const formData = new FormData();
    formData.append('image', file);
    
    fetch('/api/image/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            displayImageAnalysis(data.analysis);
            showToast('Image analyzed successfully!', 'success');
        } else {
            showToast(data.error || 'Failed to analyze image', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showToast('Network error. Please try again.', 'error');
    });
}

function displayImageAnalysis(analysis) {
    analysisContent.innerHTML = `
        <div class="analysis-section">
            <h5>Description</h5>
            <p>${analysis.description}</p>
        </div>
        <div class="analysis-section">
            <h5>Relevant Concepts</h5>
            <ul>
                ${analysis.relevant_concepts.map(concept => `<li>${concept}</li>`).join('')}
            </ul>
        </div>
        <div class="analysis-section">
            <h5>Learning Suggestions</h5>
            <p>${analysis.suggestions}</p>
        </div>
    `;
    
    imageAnalysis.classList.remove('hidden');
}

function loadProgress() {
    fetch('/api/progress/get')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayProgress(data.progress);
        } else {
            showToast(data.error || 'Failed to load progress', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Network error. Please try again.', 'error');
    });
}

function displayProgress(progress) {
    const completed = progress.filter(p => p.completed).length;
    const totalTime = progress.reduce((sum, p) => sum + p.time_spent, 0);
    const averageScoreValue = completed > 0 ? 
        progress.filter(p => p.completed).reduce((sum, p) => sum + p.score, 0) / completed : 0;
    
    lessonsCompleted.textContent = completed;
    totalStudyTime.textContent = `${totalTime} min`;
    averageScore.textContent = completed > 0 ? `${Math.round(averageScoreValue)}%` : '-';
    
    // Display progress history
    progressHistory.innerHTML = '<h4>Recent Lessons</h4>';
    
    if (progress.length === 0) {
        progressHistory.innerHTML += '<p>No lessons completed yet. Start learning to see your progress here!</p>';
        return;
    }
    
    progress.forEach(item => {
        const progressItem = document.createElement('div');
        progressItem.className = 'progress-item';
        
        const statusClass = item.completed ? 'completed' : 'in-progress';
        const statusText = item.completed ? 'Completed' : 'In Progress';
        
        progressItem.innerHTML = `
            <div>
                <div class="topic">${item.topic}</div>
                <div>Difficulty: Level ${item.difficulty_level}</div>
            </div>
            <div>
                <div class="status ${statusClass}">${statusText}</div>
                ${item.completed ? `<div>Score: ${item.score}%</div>` : ''}
                <div>Time: ${item.time_spent} min</div>
            </div>
        `;
        
        progressHistory.appendChild(progressItem);
    });
}

function showLoading(text = 'Loading...') {
    loadingText.textContent = text;
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    const toastContainer = document.getElementById('toastContainer');
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toastContainer.contains(toast)) {
            toastContainer.removeChild(toast);
        }
    }, 5000);
    
    // Click to dismiss
    toast.addEventListener('click', () => {
        if (toastContainer.contains(toast)) {
            toastContainer.removeChild(toast);
        }
    });
}

// Quiz Functions
function checkQuizAvailability() {
    if (currentLesson && currentLesson.lesson_id) {
        // Check if lesson is completed
        fetch('/api/quiz/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ lesson_id: currentLesson.lesson_id })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.quiz_available) {
                showQuizInterface();
                if (!currentQuiz) {
                    startQuiz();
                }
            } else {
                showQuizNotAvailable();
            }
        })
        .catch(error => {
            console.error('Error checking quiz availability:', error);
            showQuizNotAvailable();
        });
    } else {
        showQuizNotAvailable();
    }
}

function showQuizNotAvailable() {
    quizNotAvailable.classList.remove('hidden');
    quizAvailable.classList.add('hidden');
}

function showQuizInterface() {
    quizNotAvailable.classList.add('hidden');
    quizAvailable.classList.remove('hidden');
    
    if (currentLesson) {
        quizTopic.textContent = currentLesson.topic;
        quizDifficulty.textContent = `Level ${currentLesson.difficulty}`;
    }
}

function startQuiz() {
    if (!currentLesson || !currentLesson.lesson_id) {
        showToast('No lesson available for quiz', 'error');
        return;
    }
    
    showLoading('Generating quiz questions...');
    quizStartTime = Date.now();
    
    fetch('/api/quiz/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            lesson_id: currentLesson.lesson_id,
            topic: currentLesson.topic,
            difficulty: currentLesson.difficulty,
            content: currentLesson.content
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            currentQuiz = data.quiz;
            currentQuiz.currentQuestionIndex = 0;
            currentQuiz.userAnswers = [];
            currentQuiz.score = 0;
            
            totalQuestions.textContent = currentQuiz.questions.length;
            
            // Hide result and show question
            quizResult.classList.add('hidden');
            document.getElementById('quizQuestion').classList.remove('hidden');
            
            displayQuestion();
            showToast('Quiz generated successfully!', 'success');
        } else {
            showToast(data.error || 'Failed to generate quiz', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showToast('Network error. Please try again.', 'error');
    });
}

function displayQuestion() {
    if (!currentQuiz || !currentQuiz.questions) return;
    
    const question = currentQuiz.questions[currentQuiz.currentQuestionIndex];
    currentQuestion.textContent = currentQuiz.currentQuestionIndex + 1;
    
    questionText.textContent = question.question;
    
    // Clear previous options
    questionOptions.innerHTML = '';
    
    // Create option elements
    question.options.forEach((option, index) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option-item';
        optionDiv.dataset.optionIndex = index;
        
        optionDiv.innerHTML = `
            <div class="option-letter">${String.fromCharCode(65 + index)}</div>
            <div class="option-text">${option}</div>
        `;
        
        optionDiv.addEventListener('click', () => selectOption(index));
        questionOptions.appendChild(optionDiv);
    });
    
    // Reset button states
    submitAnswerBtn.disabled = true;
    nextQuestionBtn.classList.add('hidden');
    
    // Clear any previous selections
    document.querySelectorAll('.option-item').forEach(opt => {
        opt.classList.remove('selected', 'correct', 'incorrect');
    });
}

function selectOption(optionIndex) {
    // Clear previous selections
    document.querySelectorAll('.option-item').forEach(opt => {
        opt.classList.remove('selected');
    });
    
    // Select current option
    const selectedOption = document.querySelector(`[data-option-index="${optionIndex}"]`);
    selectedOption.classList.add('selected');
    
    // Enable submit button
    submitAnswerBtn.disabled = false;
    
    // Store selected answer
    currentQuiz.selectedAnswer = optionIndex;
}

function submitQuizAnswer() {
    if (currentQuiz.selectedAnswer === undefined) return;
    
    const question = currentQuiz.questions[currentQuiz.currentQuestionIndex];
    const isCorrect = currentQuiz.selectedAnswer === question.correctAnswer;
    
    // Store user answer
    currentQuiz.userAnswers[currentQuiz.currentQuestionIndex] = {
        selected: currentQuiz.selectedAnswer,
        correct: question.correctAnswer,
        isCorrect: isCorrect
    };
    
    if (isCorrect) {
        currentQuiz.score++;
    }
    
    // Show correct/incorrect feedback
    document.querySelectorAll('.option-item').forEach((opt, index) => {
        if (index === question.correctAnswer) {
            opt.classList.add('correct');
        } else if (index === currentQuiz.selectedAnswer && index !== question.correctAnswer) {
            opt.classList.add('incorrect');
        }
    });
    
    // Disable submit button and show next button
    submitAnswerBtn.disabled = true;
    
    if (currentQuiz.currentQuestionIndex < currentQuiz.questions.length - 1) {
        nextQuestionBtn.classList.remove('hidden');
        nextQuestionBtn.innerHTML = '<i class="fas fa-arrow-right"></i> Next Question';
    } else {
        nextQuestionBtn.classList.remove('hidden');
        nextQuestionBtn.innerHTML = '<i class="fas fa-flag-checkered"></i> Finish Quiz';
    }
    
    // Clear selected answer for next question
    currentQuiz.selectedAnswer = undefined;
}

function nextQuizQuestion() {
    currentQuiz.currentQuestionIndex++;
    
    if (currentQuiz.currentQuestionIndex < currentQuiz.questions.length) {
        displayQuestion();
    } else {
        finishQuiz();
    }
}

function finishQuiz() {
    const quizDuration = Math.floor((Date.now() - quizStartTime) / 1000);
    const percentage = Math.round((currentQuiz.score / currentQuiz.questions.length) * 100);
    
    // Hide question interface and show results
    document.getElementById('quizQuestion').classList.add('hidden');
    quizResult.classList.remove('hidden');
    
    // Display results
    finalScore.textContent = `${currentQuiz.score}/${currentQuiz.questions.length}`;
    finalPercentage.textContent = `${percentage}%`;
    quizTime.textContent = `${quizDuration} seconds`;
    
    // Generate feedback
    let feedback = '';
    if (percentage >= 90) {
        feedback = '🎉 Excellent work! You have mastered this topic. Your understanding is outstanding!';
    } else if (percentage >= 75) {
        feedback = '👏 Great job! You have a solid understanding of the topic. Keep up the good work!';
    } else if (percentage >= 60) {
        feedback = '👍 Good effort! You understand most concepts. Review the lesson to strengthen your knowledge.';
    } else {
        feedback = '📚 Keep studying! Consider reviewing the lesson material and try the quiz again.';
    }
    
    quizFeedback.innerHTML = `<h4>Feedback</h4><p>${feedback}</p>`;
    
    // Save quiz results
    saveQuizResults(percentage, quizDuration);
    
    showToast(`Quiz completed! You scored ${percentage}%`, percentage >= 75 ? 'success' : 'info');
}

function saveQuizResults(percentage, duration) {
    if (!currentLesson || !currentLesson.lesson_id) return;
    
    fetch('/api/quiz/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            lesson_id: currentLesson.lesson_id,
            score: percentage,
            total_questions: currentQuiz.questions.length,
            correct_answers: currentQuiz.score,
            time_taken: duration,
            answers: currentQuiz.userAnswers
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Quiz results saved successfully');
        } else {
            console.error('Failed to save quiz results:', data.error);
        }
    })
    .catch(error => {
        console.error('Error saving quiz results:', error);
    });
}