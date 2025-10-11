import json
import boto3
import logging
from typing import Dict, Any, List
import os
import requests
from datetime import datetime

class BedrockAgent:
    """Unified AI agent for travel companion functionality"""
    
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime')
        self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        self.dynamodb_client = boto3.client('dynamodb')
        self.s3_client = boto3.client('s3')
        
    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process user message and determine appropriate action"""
        try:
            # Get user context
            user_context = self._get_user_context(user_id)
            
            # Determine intent from message
            intent = self._classify_intent(message)
            
            # Process based on intent
            response = self._handle_intent(intent, message, user_id, user_context)
            
            # Save interaction to DynamoDB
            self._save_interaction(user_id, message, response)
            
            return response
            
        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
            return {
                'text': "I'm sorry, I encountered an error processing your request. Please try again.",
                'type': 'error'
            }
    
    def _classify_intent(self, message: str) -> str:
        """Classify user intent using LLM"""
        prompt = f"""
        Classify the following travel-related message into one of these categories:
        - flight_booking: booking flights
        - hotel_booking: booking hotels  
        - itinerary_planning: creating or modifying travel plans
        - translation: translating text or asking for language help
        - weather_alerts: asking about weather or travel alerts
        - document_management: managing travel documents
        - general_travel: general travel questions or conversation
        
        Message: "{message}"
        
        Respond with only the category name.
        """
        
        response = self._call_bedrock(prompt)
        return response.strip().lower()
    
    def _handle_intent(self, intent: str, message: str, user_id: str, context: Dict) -> Dict[str, Any]:
        """Handle different user intents"""
        
        if intent == 'flight_booking':
            return self._handle_flight_booking(message, user_id)
        elif intent == 'hotel_booking':
            return self._handle_hotel_booking(message, user_id)
        elif intent == 'itinerary_planning':
            return self._handle_itinerary_planning(message, user_id, context)
        elif intent == 'translation':
            return self._handle_translation(message)
        elif intent == 'weather_alerts':
            return self._handle_weather_alerts(message, user_id)
        elif intent == 'document_management':
            return self._handle_document_management(message, user_id)
        else:
            return self._handle_general_travel(message, context)
    
    def _handle_flight_booking(self, message: str, user_id: str) -> Dict[str, Any]:
        """Handle flight booking requests"""
        prompt = f"""
        Extract flight booking details from this message: "{message}"
        
        Extract:
        - Departure city/airport
        - Destination city/airport  
        - Departure date
        - Return date (if round trip)
        - Number of passengers
        - Class preference
        
        Respond in JSON format with extracted information and any missing details needed.
        """
        
        extraction = self._call_bedrock(prompt)
        
        try:
            flight_data = json.loads(extraction)
            # Here you would integrate with flight booking API
            return {
                'text': f"I found flight options for you. Let me search for flights from {flight_data.get('departure')} to {flight_data.get('destination')}.",
                'type': 'flight_booking',
                'data': flight_data,
                'action_required': 'search_flights'
            }
        except:
            return {
                'text': "I understand you want to book a flight. Could you please provide more details like departure city, destination, and travel dates?",
                'type': 'clarification'
            }
    
    def _handle_hotel_booking(self, message: str, user_id: str) -> Dict[str, Any]:
        """Handle hotel booking requests"""
        prompt = f"""
        Extract hotel booking details from: "{message}"
        
        Extract:
        - City/location
        - Check-in date
        - Check-out date
        - Number of guests
        - Room preferences
        - Budget range
        
        Respond in JSON format.
        """
        
        extraction = self._call_bedrock(prompt)
        
        try:
            hotel_data = json.loads(extraction)
            return {
                'text': f"I'll help you find hotels in {hotel_data.get('location')} for your stay.",
                'type': 'hotel_booking',
                'data': hotel_data,
                'action_required': 'search_hotels'
            }
        except:
            return {
                'text': "I can help you find hotels. Please let me know the city, dates, and number of guests.",
                'type': 'clarification'
            }
    
    def _handle_itinerary_planning(self, message: str, user_id: str, context: Dict) -> Dict[str, Any]:
        """Handle itinerary planning requests"""
        prompt = f"""
        Create a travel itinerary based on this request: "{message}"
        
        Consider:
        - Destination(s)
        - Duration of stay
        - Interests/preferences
        - Budget considerations
        - Travel dates
        
        Provide a detailed day-by-day itinerary with activities, restaurants, and tips.
        """
        
        itinerary = self._call_bedrock(prompt)
        
        return {
            'text': itinerary,
            'type': 'itinerary',
            'action_required': 'save_itinerary'
        }
    
    def _handle_translation(self, message: str) -> Dict[str, Any]:
        """Handle translation requests"""
        prompt = f"""
        Handle this translation request: "{message}"
        
        If it's a translation request, identify:
        - Text to translate
        - Source language (if specified)
        - Target language
        
        If it's asking for language help, provide helpful phrases for travelers.
        """
        
        response = self._call_bedrock(prompt)
        
        return {
            'text': response,
            'type': 'translation'
        }
    
    def _handle_weather_alerts(self, message: str, user_id: str) -> Dict[str, Any]:
        """Handle weather and alerts requests"""
        prompt = f"""
        Handle this weather/alert request: "{message}"
        
        Identify what location and type of information is needed.
        Provide helpful travel weather advice.
        """
        
        response = self._call_bedrock(prompt)
        
        return {
            'text': response,
            'type': 'weather_alerts',
            'action_required': 'check_weather'
        }
    
    def _handle_document_management(self, message: str, user_id: str) -> Dict[str, Any]:
        """Handle document management requests"""
        return {
            'text': "I can help you manage your travel documents. You can upload tickets, passports, or other travel documents securely.",
            'type': 'document_management',
            'action_required': 'document_action'
        }
    
    def _handle_general_travel(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle general travel conversation"""
        prompt = f"""
        You are a helpful travel companion AI. Respond to this travel-related message: "{message}"
        
        Provide helpful, accurate travel advice and maintain a friendly, conversational tone.
        Consider the user's context: {json.dumps(context)}
        """
        
        response = self._call_bedrock(prompt)
        
        return {
            'text': response,
            'type': 'general'
        }
    
    def _call_bedrock(self, prompt: str) -> str:
        """Make a call to Bedrock LLM"""
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            logging.error(f"Bedrock API error: {str(e)}")
            return "I'm having trouble processing your request right now. Please try again."
    
    def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user context from DynamoDB"""
        try:
            response = self.dynamodb_client.get_item(
                TableName='TravelItineraries',
                Key={'UserID': {'S': user_id}}
            )
            
            if 'Item' in response:
                return {
                    'current_trips': response['Item'].get('CurrentTrips', {}).get('S', '{}'),
                    'preferences': response['Item'].get('Preferences', {}).get('S', '{}'),
                    'history': response['Item'].get('History', {}).get('S', '{}')
                }
            
            return {}
            
        except Exception as e:
            logging.error(f"Error getting user context: {str(e)}")
            return {}
    
    def _save_interaction(self, user_id: str, message: str, response: Dict[str, Any]) -> None:
        """Save interaction to DynamoDB"""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            self.dynamodb_client.put_item(
                TableName='TravelInteractions',
                Item={
                    'UserID': {'S': user_id},
                    'Timestamp': {'S': timestamp},
                    'UserMessage': {'S': message},
                    'BotResponse': {'S': json.dumps(response)},
                    'TTL': {'N': str(int(datetime.utcnow().timestamp()) + 86400 * 30)}  # 30 days TTL
                }
            )
            
        except Exception as e:
            logging.error(f"Error saving interaction: {str(e)}")