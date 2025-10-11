import json
import logging
from typing import Dict, Any
from flask import jsonify
import boto3
import requests
import os

# Initialize AWS Translate client
translate_client = boto3.client('translate')

# Google Translate API (you'll need to add your API key)
GOOGLE_TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
GOOGLE_TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'

def handle_translation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle translation requests"""
    
    try:
        text = data.get('text')
        source_language = data.get('source_language', 'auto')
        target_language = data.get('target_language')
        translation_service = data.get('service', 'aws')  # 'aws' or 'google'
        
        if not text or not target_language:
            return jsonify({
                'error': 'Missing required parameters: text and target_language'
            }), 400
        
        # Route to appropriate translation service
        if translation_service == 'google' and GOOGLE_TRANSLATE_API_KEY:
            result = translate_with_google(text, source_language, target_language)
        else:
            result = translate_with_aws(text, source_language, target_language)
        
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Translation failed'}), 500
            
    except Exception as e:
        logging.error(f"Error in handle_translation: {str(e)}")
        return jsonify({'error': 'Translation service error'}), 500

def translate_with_aws(text: str, source_language: str, target_language: str) -> Dict[str, Any]:
    """Translate text using AWS Translate"""
    
    try:
        # AWS Translate doesn't support 'auto' detection directly
        if source_language == 'auto':
            # First detect the language
            source_language = detect_language_aws(text)
            if not source_language:
                source_language = 'en'  # Default to English
        
        # Translate the text
        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode=source_language,
            TargetLanguageCode=target_language
        )
        
        return {
            'translated_text': response['TranslatedText'],
            'source_language': response['SourceLanguageCode'],
            'target_language': response['TargetLanguageCode'],
            'service': 'aws_translate',
            'confidence': None  # AWS doesn't provide confidence scores
        }
        
    except Exception as e:
        logging.error(f"AWS Translate error: {str(e)}")
        return None

def translate_with_google(text: str, source_language: str, target_language: str) -> Dict[str, Any]:
    """Translate text using Google Translate API"""
    
    try:
        params = {
            'key': GOOGLE_TRANSLATE_API_KEY,
            'q': text,
            'target': target_language
        }
        
        if source_language != 'auto':
            params['source'] = source_language
        
        response = requests.post(GOOGLE_TRANSLATE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' in data and 'translations' in data['data']:
            translation = data['data']['translations'][0]
            
            return {
                'translated_text': translation['translatedText'],
                'source_language': translation.get('detectedSourceLanguage', source_language),
                'target_language': target_language,
                'service': 'google_translate',
                'confidence': None
            }
        else:
            return None
            
    except Exception as e:
        logging.error(f"Google Translate error: {str(e)}")
        return None

def detect_language_aws(text: str) -> str:
    """Detect language using AWS Comprehend"""
    
    try:
        comprehend_client = boto3.client('comprehend')
        
        response = comprehend_client.detect_dominant_language(Text=text)
        
        languages = response.get('Languages', [])
        if languages:
            # Return the language with highest confidence
            dominant_language = max(languages, key=lambda x: x['Score'])
            return dominant_language['LanguageCode']
        
        return 'en'  # Default to English
        
    except Exception as e:
        logging.error(f"Language detection error: {str(e)}")
        return 'en'

def get_travel_phrases(data: Dict[str, Any]) -> Dict[str, Any]:
    """Get common travel phrases in a specific language"""
    
    try:
        target_language = data.get('target_language')
        category = data.get('category', 'general')
        
        if not target_language:
            return jsonify({'error': 'Missing target_language'}), 400
        
        # Common travel phrases by category
        phrase_categories = {
            'general': [
                "Hello", "Thank you", "Please", "Excuse me", "I'm sorry",
                "Do you speak English?", "I don't understand", "Help me",
                "Where is...?", "How much does this cost?"
            ],
            'transportation': [
                "Where is the train station?", "Where is the bus stop?",
                "I need a taxi", "To the airport, please", "What time does it leave?",
                "Is this seat taken?", "Where do I buy tickets?", "Platform number"
            ],
            'accommodation': [
                "I have a reservation", "Check in", "Check out",
                "Where is my room?", "I need help with my luggage",
                "Is breakfast included?", "Wi-Fi password", "Room service"
            ],
            'dining': [
                "Table for two", "Menu, please", "I'm vegetarian",
                "The check, please", "Is service included?", "Water, please",
                "What do you recommend?", "I have allergies"
            ],
            'emergency': [
                "Call the police", "I need a doctor", "Where is the hospital?",
                "I lost my passport", "I need help", "Emergency",
                "Call an ambulance", "I'm lost"
            ]
        }
        
        phrases = phrase_categories.get(category, phrase_categories['general'])
        
        # Translate all phrases
        translated_phrases = []
        
        for phrase in phrases:
            result = translate_with_aws(phrase, 'en', target_language)
            if result:
                translated_phrases.append({
                    'english': phrase,
                    'translated': result['translated_text'],
                    'language': target_language
                })
        
        return jsonify({
            'category': category,
            'language': target_language,
            'phrases': translated_phrases,
            'count': len(translated_phrases)
        })
        
    except Exception as e:
        logging.error(f"Error getting travel phrases: {str(e)}")
        return jsonify({'error': 'Travel phrases service error'}), 500

def translate_document_text(data: Dict[str, Any]) -> Dict[str, Any]:
    """Translate text extracted from documents"""
    
    try:
        user_id = data.get('user_id')
        document_key = data.get('document_key')
        target_language = data.get('target_language')
        
        if not all([user_id, document_key, target_language]):
            return jsonify({
                'error': 'Missing required parameters: user_id, document_key, target_language'
            }), 400
        
        # Extract text from document (this would typically use AWS Textract)
        extracted_text = extract_text_from_document(document_key)
        
        if not extracted_text:
            return jsonify({'error': 'Could not extract text from document'}), 400
        
        # Translate the extracted text
        result = translate_with_aws(extracted_text, 'auto', target_language)
        
        if result:
            return jsonify({
                'document_key': document_key,
                'original_text': extracted_text,
                'translated_text': result['translated_text'],
                'source_language': result['source_language'],
                'target_language': result['target_language']
            })
        else:
            return jsonify({'error': 'Translation failed'}), 500
            
    except Exception as e:
        logging.error(f"Error translating document: {str(e)}")
        return jsonify({'error': 'Document translation error'}), 500

def extract_text_from_document(document_key: str) -> str:
    """Extract text from document using AWS Textract (simplified version)"""
    
    try:
        # This is a simplified version - in production you'd use AWS Textract
        # For now, return a mock response
        return "Sample document text that would be extracted using AWS Textract"
        
    except Exception as e:
        logging.error(f"Error extracting text from document: {str(e)}")
        return None

def get_supported_languages() -> Dict[str, Any]:
    """Get list of supported languages for translation"""
    
    try:
        # AWS Translate supported languages (major ones)
        aws_languages = {
            'af': 'Afrikaans',
            'sq': 'Albanian',
            'am': 'Amharic',
            'ar': 'Arabic',
            'hy': 'Armenian',
            'az': 'Azerbaijani',
            'bn': 'Bengali',
            'bs': 'Bosnian',
            'bg': 'Bulgarian',
            'ca': 'Catalan',
            'zh': 'Chinese (Simplified)',
            'zh-TW': 'Chinese (Traditional)',
            'hr': 'Croatian',
            'cs': 'Czech',
            'da': 'Danish',
            'nl': 'Dutch',
            'en': 'English',
            'et': 'Estonian',
            'fa': 'Farsi (Persian)',
            'tl': 'Filipino',
            'fi': 'Finnish',
            'fr': 'French',
            'fr-CA': 'French (Canada)',
            'ka': 'Georgian',
            'de': 'German',
            'el': 'Greek',
            'gu': 'Gujarati',
            'ht': 'Haitian Creole',
            'ha': 'Hausa',
            'he': 'Hebrew',
            'hi': 'Hindi',
            'hu': 'Hungarian',
            'is': 'Icelandic',
            'id': 'Indonesian',
            'it': 'Italian',
            'ja': 'Japanese',
            'kn': 'Kannada',
            'kk': 'Kazakh',
            'ko': 'Korean',
            'lv': 'Latvian',
            'lt': 'Lithuanian',
            'mk': 'Macedonian',
            'ms': 'Malay',
            'ml': 'Malayalam',
            'mt': 'Maltese',
            'mn': 'Mongolian',
            'no': 'Norwegian',
            'ps': 'Pashto',
            'pl': 'Polish',
            'pt': 'Portuguese',
            'pt-PT': 'Portuguese (Portugal)',
            'pa': 'Punjabi',
            'ro': 'Romanian',
            'ru': 'Russian',
            'sr': 'Serbian',
            'si': 'Sinhala',
            'sk': 'Slovak',
            'sl': 'Slovenian',
            'so': 'Somali',
            'es': 'Spanish',
            'es-MX': 'Spanish (Mexico)',
            'sw': 'Swahili',
            'sv': 'Swedish',
            'ta': 'Tamil',
            'te': 'Telugu',
            'th': 'Thai',
            'tr': 'Turkish',
            'uk': 'Ukrainian',
            'ur': 'Urdu',
            'uz': 'Uzbek',
            'vi': 'Vietnamese',
            'cy': 'Welsh'
        }
        
        return jsonify({
            'languages': aws_languages,
            'count': len(aws_languages),
            'service': 'aws_translate'
        })
        
    except Exception as e:
        logging.error(f"Error getting supported languages: {str(e)}")
        return jsonify({'error': 'Language service error'}), 500

def save_translation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save a translation for later reference"""
    
    try:
        from dynamodb_client import DynamoDBClient
        
        user_id = data.get('user_id')
        translation_data = data.get('translation')
        
        if not user_id or not translation_data:
            return jsonify({'error': 'Missing user_id or translation data'}), 400
        
        dynamodb_client = DynamoDBClient()
        
        # Get user data
        user_data = dynamodb_client.get_user_data(user_id) or {}
        saved_translations = user_data.get('saved_translations', [])
        
        # Add new translation
        translation_entry = {
            'id': f"trans_{int(datetime.utcnow().timestamp())}",
            'original_text': translation_data.get('original_text'),
            'translated_text': translation_data.get('translated_text'),
            'source_language': translation_data.get('source_language'),
            'target_language': translation_data.get('target_language'),
            'saved_at': datetime.utcnow().isoformat()
        }
        
        saved_translations.append(translation_entry)
        
        # Keep only last 50 translations
        if len(saved_translations) > 50:
            saved_translations = saved_translations[-50:]
        
        user_data['saved_translations'] = saved_translations
        
        success = dynamodb_client.save_user_data(user_id, user_data)
        
        if success:
            return jsonify({
                'message': 'Translation saved successfully',
                'translation_id': translation_entry['id']
            })
        else:
            return jsonify({'error': 'Failed to save translation'}), 500
            
    except Exception as e:
        logging.error(f"Error saving translation: {str(e)}")
        return jsonify({'error': 'Translation save error'}), 500

def get_saved_translations(user_id: str) -> Dict[str, Any]:
    """Get user's saved translations"""
    
    try:
        from dynamodb_client import DynamoDBClient
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        dynamodb_client = DynamoDBClient()
        user_data = dynamodb_client.get_user_data(user_id)
        
        if not user_data:
            return jsonify({
                'translations': [],
                'count': 0
            })
        
        saved_translations = user_data.get('saved_translations', [])
        
        return jsonify({
            'translations': saved_translations,
            'count': len(saved_translations)
        })
        
    except Exception as e:
        logging.error(f"Error getting saved translations: {str(e)}")
        return jsonify({'error': 'Saved translations retrieval error'}), 500