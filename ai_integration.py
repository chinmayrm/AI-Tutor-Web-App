"""
AI Integration Module for Personal Tutor
Uses OpenRouter with Meta Llama 3.3 8B Instruct (free)
"""

import os
import requests
import json
import base64
from typing import Dict, Any, Optional

class AIService:
    """Base class for AI service integrations"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = None
    
    def generate_lesson(self, topic: str, difficulty: int) -> str:
        """Generate lesson content"""
        raise NotImplementedError
    
    def chat_response(self, message: str, context: str = "") -> str:
        """Generate chat response"""
        raise NotImplementedError
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image content"""
        raise NotImplementedError
    
    def generate_quiz(self, topic: str, difficulty: int, content: str = "") -> Dict[str, Any]:
        """Generate quiz questions"""
        raise NotImplementedError
    
    def generate_diagram(self, concept: str, diagram_type: str = "flowchart") -> str:
        """Generate ASCII diagram for a concept"""
        raise NotImplementedError
    
    def _fallback_lesson(self, topic: str, difficulty: int) -> str:
        """Fallback lesson content when AI is unavailable"""
        return f"""
# Learning About: {topic}

## Introduction
Welcome to your personalized lesson on **{topic}**! This lesson is designed to help you understand the key concepts and practical applications at difficulty level {difficulty}.

## Key Concepts

### Foundation
Understanding {topic} starts with grasping its fundamental principles. This topic is important because it connects to many real-world applications and can enhance your knowledge in related areas.

### Core Elements
1. **Basic Definition**: {topic} encompasses several important aspects that we'll explore
2. **Key Components**: Breaking down the main parts helps build understanding
3. **Relationships**: How {topic} connects to other concepts you may already know

## Practical Applications
{topic} is used in various real-world scenarios:
- Everyday applications that you might encounter
- Professional or academic contexts
- Problem-solving situations

## Interactive Learning
Think about these questions as you learn:
- How does {topic} relate to your personal interests?
- Where have you encountered {topic} before?
- What questions do you have about {topic}?

## Summary
By understanding {topic}, you're building valuable knowledge that can be applied in many situations. The key takeaways include the fundamental concepts, practical applications, and connections to other areas of learning.

**Remember**: Learning is a journey, and every question you ask helps deepen your understanding!
"""
    
    def _fallback_chat(self, message: str) -> str:
        """Fallback chat response when AI is unavailable"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['what', 'how', 'why', 'when', 'where']):
            return f"That's a great question about '{message}'. Based on educational principles, I'd suggest breaking this down into smaller parts. What specific aspect would you like to explore first? This approach helps build understanding step by step."
        
        elif any(word in message_lower for word in ['explain', 'tell me', 'describe']):
            return f"I'd be happy to help explain that! When learning about '{message}', it's helpful to start with the basics and build up. Think about what you already know about this topic and how it might connect to new information."
        
        elif any(word in message_lower for word in ['help', 'stuck', 'confused', 'difficult']):
            return "I understand that learning can sometimes be challenging! Here are some strategies that often help: 1) Break the problem into smaller pieces, 2) Connect new information to what you already know, 3) Ask specific questions about the parts that confuse you. What specific part would you like to focus on?"
        
        else:
            return f"Thank you for sharing that thought about '{message}'. Learning is most effective when we engage actively with the material. How do you think this connects to what we've been discussing? What questions does this raise for you?"
    
    def _fallback_image_analysis(self) -> Dict[str, Any]:
        """Fallback image analysis when AI is unavailable"""
        return {
            'description': 'This image contains visual content that can support your learning. While I cannot analyze the specific details right now, images are powerful learning tools that can help reinforce concepts.',
            'relevant_concepts': ['Visual learning', 'Image interpretation', 'Multimedia education'],
            'suggestions': 'Consider how this image relates to your current lesson. What details do you notice? How might they connect to the concepts you are studying? Visual elements often provide additional context and examples.'
        }

class OpenRouterService(AIService):
    """OpenRouter integration with Meta Llama 3.3 8B Instruct (free)"""
    
    def __init__(self):
        super().__init__()
        # Use the provided API key directly
        self.api_key = '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'
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "meta-llama/llama-3.3-70b-instruct:free"
        self.app_name = "AI Personal Tutor"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_lesson(self, topic: str, difficulty: int) -> str:
        if not self.is_available():
            return self._fallback_lesson(topic, difficulty)
        
        try:
            difficulty_map = {
                1: "beginner-friendly with simple explanations and basic concepts",
                2: "elementary level with clear examples and step-by-step explanations",
                3: "intermediate level with detailed explanations and practical applications",
                4: "advanced level with complex concepts and in-depth analysis",
                5: "expert level with sophisticated analysis and advanced applications"
            }
            
            prompt = f"""Create a comprehensive, visually engaging educational lesson about {topic} for a {difficulty_map.get(difficulty, 'intermediate')} learner.

Use rich HTML formatting to make the lesson visually appealing:

FORMATTING REQUIREMENTS:
- Use <h1>, <h2>, <h3> for clear headings hierarchy
- Use <strong> for important terms and <em> for emphasis
- Use <ul>/<ol> for organized lists
- Use <blockquote> for key quotes or important concepts
- Use <code> for technical terms or examples
- Use <div class="highlight"> for important information
- Use <div class="example"> for practical examples
- Use <div class="question"> for interactive questions
- Use <div class="visual-note"> for visual learning elements

STRUCTURE THE LESSON:
1. **Engaging Introduction** - Hook the learner with an interesting opening
2. **Learning Objectives** - Clear goals in a bulleted list
3. **Key Concepts** - Main content with visual hierarchy
4. **Visual Elements** - Include simple ASCII diagrams where helpful
5. **Practical Examples** - Real-world applications
6. **Interactive Questions** - Thought-provoking queries
7. **Summary & Next Steps** - Key takeaways and progression

VISUAL ENHANCEMENTS:
- Add emoji icons (📚 🎯 💡 ⭐ 🔍) to section headers
- Include simple ASCII art or diagrams where relevant (use <pre> tags for ASCII art)
- Use progress indicators like ▶️ for steps
- Add visual breaks with horizontal rules
- Include callout boxes for important information
- For complex topics, create simple ASCII diagrams or flowcharts
- Use tables for comparisons or structured data

EXAMPLE ASCII DIAGRAM (when relevant):
<pre>
    Input → [Process] → Output
      ↓        ↓         ↓
   Data    Analysis   Result
</pre>

Make it educational, visually rich, well-organized, and engaging. Target 600-900 words with rich formatting."""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-personal-tutor.com",
                "X-Title": self.app_name
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an expert educational content creator who makes engaging, personalized lessons. Create well-structured, informative content that helps students learn effectively."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 1200,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return content
                else:
                    print(f"OpenRouter: No choices in response: {result}")
                    return self._fallback_lesson(topic, difficulty)
            else:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                return self._fallback_lesson(topic, difficulty)
                
        except Exception as e:
            print(f"OpenRouter error: {e}")
            return self._fallback_lesson(topic, difficulty)
    
    def chat_response(self, message: str, context: str = "") -> str:
        if not self.is_available():
            return self._fallback_chat(message)
        
        try:
            system_prompt = "You are a helpful AI tutor. Answer questions clearly, educationally, and encouragingly. Provide explanations that help students understand concepts better."
            if context:
                system_prompt += f" Current lesson context: {context[:400]}..."
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-personal-tutor.com",
                "X-Title": self.app_name
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": message
                    }
                ],
                "max_tokens": 600,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    return self._fallback_chat(message)
            else:
                print(f"OpenRouter chat error: {response.status_code} - {response.text}")
                return self._fallback_chat(message)
                
        except Exception as e:
            print(f"OpenRouter chat error: {e}")
            return self._fallback_chat(message)
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        # Llama 3.3 8B doesn't have vision capabilities, so we'll provide a text-based analysis prompt
        try:
            # Read image and get basic info
            file_size = os.path.getsize(image_path)
            file_ext = image_path.lower().split('.')[-1]
            
            # Create an educational analysis based on the context
            analysis_prompt = f"""As an educational AI, provide an analysis for an uploaded image file (format: {file_ext}, size: {file_size} bytes). 

Since I cannot see the actual image content, provide a helpful educational response that:
1. Explains the educational value of visual learning
2. Suggests how images can enhance understanding of topics
3. Provides strategies for analyzing visual content
4. Encourages critical thinking about visual information

Make this response educational and encouraging for students."""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-personal-tutor.com",
                "X-Title": self.app_name
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an educational AI that helps students understand how to learn from visual content."
                    },
                    {
                        "role": "user", 
                        "content": analysis_prompt
                    }
                ],
                "max_tokens": 400,
                "temperature": 0.6
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    ai_response = result['choices'][0]['message']['content']
                    
                    return {
                        'description': ai_response,
                        'relevant_concepts': ['Visual learning', 'Critical thinking', 'Image analysis', 'Educational media'],
                        'suggestions': 'Use this uploaded image as a learning tool. Consider what details you notice, how they relate to your study topic, and what questions the image raises for further exploration.'
                    }
                    
            return self._fallback_image_analysis()
                
        except Exception as e:
            print(f"OpenRouter image analysis error: {e}")
            return self._fallback_image_analysis()
    
    def generate_quiz(self, topic: str, difficulty: int, content: str = "") -> Dict[str, Any]:
        """Generate quiz questions based on topic and content"""
        if not self.is_available():
            return {
                "error": "AI service not available",
                "questions": [
                    {
                        "question": f"What is the main concept of {topic}?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 0
                    }
                ]
            }
        
        try:
            difficulty_map = {
                1: "very easy with basic concepts",
                2: "easy with simple applications", 
                3: "moderate with practical examples",
                4: "challenging with complex scenarios",
                5: "very difficult with advanced concepts"
            }
            
            prompt = f"""Generate exactly 5 multiple choice questions about {topic} at {difficulty_map.get(difficulty, 'moderate')} difficulty level.
{f"Base the questions on this lesson content: {content[:500]}..." if content else ""}

Return ONLY a valid JSON object with this exact structure:
{{
    "questions": [
        {{
            "question": "Question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0
        }}
    ]
}}

Requirements:
- Each question must have exactly 4 options
- correct_answer must be the index (0, 1, 2, or 3) of the correct option
- Questions should test understanding, not just memorization
- Make options plausible but clearly distinguishable
- Ensure one correct answer per question"""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-personal-tutor.com",
                "X-Title": self.app_name
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an expert quiz creator. Generate educational quiz questions in valid JSON format only."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.5,
                "top_p": 0.9
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content_text = result['choices'][0]['message']['content'].strip()
                    
                    # Try to parse JSON from the response
                    try:
                        # Find JSON content in the response
                        start_idx = content_text.find('{')
                        end_idx = content_text.rfind('}') + 1
                        
                        if start_idx != -1 and end_idx > start_idx:
                            json_content = content_text[start_idx:end_idx]
                            quiz_data = json.loads(json_content)
                            
                            # Validate the structure
                            if 'questions' in quiz_data and isinstance(quiz_data['questions'], list):
                                # Ensure we have valid questions
                                valid_questions = []
                                for q in quiz_data['questions']:
                                    if (isinstance(q, dict) and 
                                        'question' in q and 
                                        'options' in q and 
                                        'correct_answer' in q and
                                        isinstance(q['options'], list) and
                                        len(q['options']) == 4 and
                                        isinstance(q['correct_answer'], int) and
                                        0 <= q['correct_answer'] <= 3):
                                        valid_questions.append(q)
                                
                                if valid_questions:
                                    return {"questions": valid_questions}
                        
                        # If parsing fails, return fallback
                        return {
                            "error": "Failed to parse quiz format",
                            "questions": [
                                {
                                    "question": f"What is a key concept in {topic}?",
                                    "options": ["Concept A", "Concept B", "Concept C", "Concept D"],
                                    "correct_answer": 0
                                }
                            ]
                        }
                        
                    except json.JSONDecodeError as e:
                        print(f"Quiz JSON parsing error: {e}")
                        return {
                            "error": "Failed to parse quiz JSON",
                            "questions": [
                                {
                                    "question": f"What is an important aspect of {topic}?",
                                    "options": ["Aspect A", "Aspect B", "Aspect C", "Aspect D"],
                                    "correct_answer": 0
                                }
                            ]
                        }
                else:
                    return {"error": "No response from AI service"}
            else:
                print(f"OpenRouter quiz error: {response.status_code} - {response.text}")
                return {"error": f"API request failed: {response.status_code}"}
                
        except Exception as e:
            print(f"OpenRouter quiz generation error: {e}")
            return {
                "error": f"Quiz generation failed: {str(e)}",
                "questions": [
                    {
                        "question": f"What would you like to learn more about regarding {topic}?",
                        "options": ["Basic concepts", "Advanced topics", "Practical applications", "Related subjects"],
                        "correct_answer": 0
                    }
                ]
            }

class AIManager:
    """Manages AI service with OpenRouter as primary service"""
    
    def __init__(self):
        self.primary_service = OpenRouterService()
        
        if self.primary_service.is_available():
            print(f"Using OpenRouter with Meta Llama 3.3 8B Instruct (free) as AI service")
        else:
            print("OpenRouter service not available, using fallback responses")
    
    def generate_lesson(self, topic: str, difficulty: int) -> str:
        """Generate lesson using OpenRouter"""
        return self.primary_service.generate_lesson(topic, difficulty)
    
    def chat_response(self, message: str, context: str = "") -> str:
        """Generate chat response using OpenRouter"""
        return self.primary_service.chat_response(message, context)
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image using OpenRouter"""
        return self.primary_service.analyze_image(image_path)
    
    def generate_quiz(self, topic: str, difficulty: int, content: str = "") -> Dict[str, Any]:
        """Generate quiz using OpenRouter"""
        return self.primary_service.generate_quiz(topic, difficulty, content)
    
    def generate_diagram(self, concept: str, diagram_type: str = "flowchart") -> str:
        """Generate diagram using OpenRouter"""
        if hasattr(self.primary_service, 'generate_diagram'):
            return self.primary_service.generate_diagram(concept, diagram_type)
        else:
            # Fallback diagram
            return f"""
┌─────────────┐
│  {concept}   │ 
│  Overview   │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Details   │
└─────────────┘"""
    
    def get_available_services(self) -> list:
        """Return list of available services"""
        if self.primary_service.is_available():
            return ["OpenRouter (Meta Llama 3.3 8B Instruct)"]
        return ["Fallback responses"]

# Global AI manager instance
ai_manager = AIManager()