import json
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from bedrock_agent import BedrockAgent
from dynamodb_client import DynamoDBClient
from lambda_functions.bookings_handler import handle_booking
from lambda_functions.alerts_handler import handle_alerts
from lambda_functions.translation_handler import handle_translation
from lambda_functions.itinerary_handler import handle_itinerary
from lambda_functions.document_manager import handle_document

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Initialize clients
bedrock_agent = BedrockAgent()
dynamodb_client = DynamoDBClient()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint for the Travel Companion Agent"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not user_id or not message:
            return jsonify({'error': 'Missing user_id or message'}), 400
        
        # Process user message through Bedrock agent
        response = bedrock_agent.process_message(user_id, message)
        
        return jsonify({
            'response': response,
            'user_id': user_id,
            'timestamp': boto3.Session().region_name
        })
    
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/booking', methods=['POST'])
def booking():
    """Handle booking requests"""
    try:
        data = request.get_json()
        return handle_booking(data)
    except Exception as e:
        logging.error(f"Error in booking endpoint: {str(e)}")
        return jsonify({'error': 'Booking service unavailable'}), 500

@app.route('/api/alerts', methods=['GET'])
def alerts():
    """Get travel alerts for user"""
    try:
        user_id = request.args.get('user_id')
        return handle_alerts(user_id)
    except Exception as e:
        logging.error(f"Error in alerts endpoint: {str(e)}")
        return jsonify({'error': 'Alerts service unavailable'}), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """Handle translation requests"""
    try:
        data = request.get_json()
        return handle_translation(data)
    except Exception as e:
        logging.error(f"Error in translation endpoint: {str(e)}")
        return jsonify({'error': 'Translation service unavailable'}), 500

@app.route('/api/itinerary', methods=['GET', 'POST'])
def itinerary():
    """Handle itinerary operations"""
    try:
        if request.method == 'GET':
            user_id = request.args.get('user_id')
            return handle_itinerary({'action': 'get', 'user_id': user_id})
        else:
            data = request.get_json()
            return handle_itinerary(data)
    except Exception as e:
        logging.error(f"Error in itinerary endpoint: {str(e)}")
        return jsonify({'error': 'Itinerary service unavailable'}), 500

@app.route('/api/documents', methods=['POST', 'GET'])
def documents():
    """Handle document management"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            return handle_document(data)
        else:
            user_id = request.args.get('user_id')
            return handle_document({'action': 'list', 'user_id': user_id})
    except Exception as e:
        logging.error(f"Error in documents endpoint: {str(e)}")
        return jsonify({'error': 'Document service unavailable'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Travel Companion Agent'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)