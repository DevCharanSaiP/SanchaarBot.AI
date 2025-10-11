import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from flask import jsonify
from dynamodb_client import DynamoDBClient
from s3_client import S3Client
import boto3

# Initialize clients
dynamodb_client = DynamoDBClient()
s3_client = S3Client()

def handle_itinerary(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle itinerary operations (create, update, get, delete)"""
    
    try:
        action = data.get('action', 'get').lower()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        # Route to appropriate handler
        if action == 'create':
            return create_itinerary(user_id, data.get('itinerary_data', {}))
        elif action == 'update':
            return update_itinerary(user_id, data.get('itinerary_data', {}))
        elif action == 'get':
            return get_itinerary(user_id)
        elif action == 'delete':
            return delete_itinerary(user_id)
        elif action == 'generate':
            return generate_itinerary(user_id, data.get('preferences', {}))
        else:
            return jsonify({'error': f'Unsupported action: {action}'}), 400
            
    except Exception as e:
        logging.error(f"Error in handle_itinerary: {str(e)}")
        return jsonify({'error': 'Itinerary service error'}), 500

def create_itinerary(user_id: str, itinerary_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new itinerary"""
    
    try:
        # Validate required fields
        required_fields = ['destination', 'start_date', 'end_date']
        for field in required_fields:
            if field not in itinerary_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create itinerary structure
        itinerary = {
            'id': f"itinerary_{int(datetime.utcnow().timestamp())}",
            'user_id': user_id,
            'destination': itinerary_data['destination'],
            'start_date': itinerary_data['start_date'],
            'end_date': itinerary_data['end_date'],
            'title': itinerary_data.get('title', f"Trip to {itinerary_data['destination']}"),
            'description': itinerary_data.get('description', ''),
            'days': itinerary_data.get('days', []),
            'budget': itinerary_data.get('budget', {}),
            'travelers': itinerary_data.get('travelers', 1),
            'preferences': itinerary_data.get('preferences', {}),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'status': 'draft'
        }
        
        # Calculate trip duration
        start_date = datetime.fromisoformat(itinerary['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(itinerary['end_date'].replace('Z', '+00:00'))
        duration = (end_date - start_date).days + 1
        itinerary['duration_days'] = duration
        
        # If no days structure provided, create default structure
        if not itinerary['days']:
            itinerary['days'] = create_default_day_structure(duration, itinerary['destination'])
        
        # Save to DynamoDB
        success = dynamodb_client.save_itinerary(user_id, itinerary)
        
        if success:
            return jsonify({
                'message': 'Itinerary created successfully',
                'itinerary': itinerary
            })
        else:
            return jsonify({'error': 'Failed to create itinerary'}), 500
            
    except Exception as e:
        logging.error(f"Error creating itinerary: {str(e)}")
        return jsonify({'error': 'Itinerary creation error'}), 500

def update_itinerary(user_id: str, itinerary_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing itinerary"""
    
    try:
        # Get existing itinerary
        existing_itinerary = dynamodb_client.get_itinerary(user_id)
        
        if not existing_itinerary:
            return jsonify({'error': 'Itinerary not found'}), 404
        
        # Update fields
        updatable_fields = [
            'title', 'description', 'days', 'budget', 'travelers', 
            'preferences', 'destination', 'start_date', 'end_date'
        ]
        
        for field in updatable_fields:
            if field in itinerary_data:
                existing_itinerary[field] = itinerary_data[field]
        
        existing_itinerary['updated_at'] = datetime.utcnow().isoformat()
        
        # Recalculate duration if dates changed
        if 'start_date' in itinerary_data or 'end_date' in itinerary_data:
            start_date = datetime.fromisoformat(existing_itinerary['start_date'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(existing_itinerary['end_date'].replace('Z', '+00:00'))
            duration = (end_date - start_date).days + 1
            existing_itinerary['duration_days'] = duration
        
        # Save updated itinerary
        success = dynamodb_client.save_itinerary(user_id, existing_itinerary)
        
        if success:
            return jsonify({
                'message': 'Itinerary updated successfully',
                'itinerary': existing_itinerary
            })
        else:
            return jsonify({'error': 'Failed to update itinerary'}), 500
            
    except Exception as e:
        logging.error(f"Error updating itinerary: {str(e)}")
        return jsonify({'error': 'Itinerary update error'}), 500

def get_itinerary(user_id: str) -> Dict[str, Any]:
    """Get user's current itinerary"""
    
    try:
        itinerary = dynamodb_client.get_itinerary(user_id)
        
        if itinerary:
            return jsonify({
                'itinerary': itinerary,
                'found': True
            })
        else:
            return jsonify({
                'message': 'No itinerary found',
                'found': False
            })
            
    except Exception as e:
        logging.error(f"Error getting itinerary: {str(e)}")
        return jsonify({'error': 'Itinerary retrieval error'}), 500

def delete_itinerary(user_id: str) -> Dict[str, Any]:
    """Delete user's itinerary"""
    
    try:
        # Get existing itinerary first
        existing_itinerary = dynamodb_client.get_itinerary(user_id)
        
        if not existing_itinerary:
            return jsonify({'error': 'Itinerary not found'}), 404
        
        # Archive the itinerary instead of deleting
        archived_itinerary = existing_itinerary.copy()
        archived_itinerary['status'] = 'archived'
        archived_itinerary['archived_at'] = datetime.utcnow().isoformat()
        
        # Save archived version
        user_data = dynamodb_client.get_user_data(user_id) or {}
        archived_itineraries = user_data.get('archived_itineraries', [])
        archived_itineraries.append(archived_itinerary)
        user_data['archived_itineraries'] = archived_itineraries[-10:]  # Keep last 10
        
        dynamodb_client.save_user_data(user_id, user_data)
        
        # Remove current itinerary
        success = dynamodb_client.save_itinerary(user_id, {})
        
        if success:
            return jsonify({
                'message': 'Itinerary deleted successfully',
                'archived': True
            })
        else:
            return jsonify({'error': 'Failed to delete itinerary'}), 500
            
    except Exception as e:
        logging.error(f"Error deleting itinerary: {str(e)}")
        return jsonify({'error': 'Itinerary deletion error'}), 500

def generate_itinerary(user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an itinerary using AI based on preferences"""
    
    try:
        from bedrock_agent import BedrockAgent
        
        # Extract preferences
        destination = preferences.get('destination')
        duration = preferences.get('duration', 3)
        budget = preferences.get('budget', 'medium')
        interests = preferences.get('interests', [])
        travel_style = preferences.get('travel_style', 'balanced')
        
        if not destination:
            return jsonify({'error': 'Destination is required for itinerary generation'}), 400
        
        # Create prompt for AI generation
        prompt = f"""
        Create a detailed {duration}-day travel itinerary for {destination}.
        
        Preferences:
        - Budget: {budget}
        - Interests: {', '.join(interests) if interests else 'General sightseeing'}
        - Travel style: {travel_style}
        
        For each day, provide:
        1. Morning activity with location and estimated time
        2. Afternoon activity with location and estimated time
        3. Evening activity/dining with location and estimated time
        4. Transportation recommendations
        5. Estimated daily budget breakdown
        6. Useful tips or notes
        
        Format the response as a structured JSON with days array.
        """
        
        bedrock_agent = BedrockAgent()
        ai_response = bedrock_agent._call_bedrock(prompt)
        
        # Parse AI response (assuming it returns structured data)
        try:
            # Clean up the response to extract JSON
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                itinerary_structure = json.loads(ai_response[json_start:json_end])
            else:
                # Fallback to default structure if AI response isn't parseable
                itinerary_structure = create_default_day_structure(duration, destination)
                
        except json.JSONDecodeError:
            # Fallback to default structure
            itinerary_structure = create_default_day_structure(duration, destination)
        
        # Create complete itinerary
        start_date = preferences.get('start_date', datetime.utcnow().strftime('%Y-%m-%d'))
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = start_datetime + timedelta(days=duration - 1)
        
        generated_itinerary = {
            'id': f"itinerary_{int(datetime.utcnow().timestamp())}",
            'user_id': user_id,
            'destination': destination,
            'start_date': start_datetime.isoformat(),
            'end_date': end_datetime.isoformat(),
            'title': f"AI-Generated Trip to {destination}",
            'description': f"A {duration}-day itinerary tailored to your preferences",
            'days': itinerary_structure.get('days', []),
            'budget': {
                'total_estimated': itinerary_structure.get('total_budget', 0),
                'currency': 'USD',
                'breakdown': itinerary_structure.get('budget_breakdown', {})
            },
            'travelers': preferences.get('travelers', 1),
            'preferences': preferences,
            'duration_days': duration,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'status': 'draft',
            'generated_by_ai': True
        }
        
        # Save generated itinerary
        success = dynamodb_client.save_itinerary(user_id, generated_itinerary)
        
        if success:
            return jsonify({
                'message': 'Itinerary generated successfully',
                'itinerary': generated_itinerary,
                'ai_generated': True
            })
        else:
            return jsonify({'error': 'Failed to save generated itinerary'}), 500
            
    except Exception as e:
        logging.error(f"Error generating itinerary: {str(e)}")
        return jsonify({'error': 'Itinerary generation error'}), 500

def create_default_day_structure(duration: int, destination: str) -> List[Dict[str, Any]]:
    """Create a default day structure for an itinerary"""
    
    days = []
    
    for day_num in range(1, duration + 1):
        day = {
            'day': day_num,
            'date': (datetime.utcnow() + timedelta(days=day_num-1)).strftime('%Y-%m-%d'),
            'title': f"Day {day_num} in {destination}",
            'activities': [
                {
                    'time': '09:00',
                    'title': 'Morning Exploration',
                    'description': f"Explore the highlights of {destination}",
                    'location': destination,
                    'type': 'sightseeing',
                    'duration': '3 hours',
                    'estimated_cost': 20
                },
                {
                    'time': '14:00',
                    'title': 'Afternoon Activities',
                    'description': f"Cultural activities and local experiences",
                    'location': destination,
                    'type': 'culture',
                    'duration': '3 hours',
                    'estimated_cost': 30
                },
                {
                    'time': '19:00',
                    'title': 'Dinner and Evening',
                    'description': f"Local cuisine and evening entertainment",
                    'location': destination,
                    'type': 'dining',
                    'duration': '2 hours',
                    'estimated_cost': 40
                }
            ],
            'transportation': {
                'type': 'walking/public transport',
                'estimated_cost': 10
            },
            'total_estimated_cost': 100,
            'notes': 'Flexible timing - adjust based on your preferences'
        }
        
        days.append(day)
    
    return days

def export_itinerary_pdf(user_id: str) -> Dict[str, Any]:
    """Export itinerary as PDF"""
    
    try:
        # Get user's itinerary
        itinerary = dynamodb_client.get_itinerary(user_id)
        
        if not itinerary:
            return jsonify({'error': 'No itinerary found'}), 404
        
        # Generate PDF content (simplified - in production use a proper PDF library)
        pdf_content = generate_itinerary_pdf_content(itinerary)
        
        # Save PDF to S3
        pdf_key = s3_client.save_itinerary_pdf(user_id, pdf_content.encode('utf-8'))
        
        if pdf_key:
            # Generate download URL
            download_url = s3_client.get_document_url(pdf_key, expires_in=3600)
            
            return jsonify({
                'message': 'Itinerary PDF generated successfully',
                'download_url': download_url,
                'pdf_key': pdf_key
            })
        else:
            return jsonify({'error': 'Failed to generate PDF'}), 500
            
    except Exception as e:
        logging.error(f"Error exporting itinerary PDF: {str(e)}")
        return jsonify({'error': 'PDF export error'}), 500

def generate_itinerary_pdf_content(itinerary: Dict[str, Any]) -> str:
    """Generate PDF content for itinerary (simplified HTML version)"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{itinerary.get('title', 'Travel Itinerary')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
            .day {{ margin: 20px 0; border: 1px solid #ddd; padding: 15px; }}
            .activity {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; }}
            .cost {{ color: #2e7d32; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{itinerary.get('title', 'Travel Itinerary')}</h1>
            <p>Destination: {itinerary.get('destination', 'N/A')}</p>
            <p>Duration: {itinerary.get('start_date', '')} to {itinerary.get('end_date', '')}</p>
            <p>Travelers: {itinerary.get('travelers', 1)}</p>
        </div>
    """
    
    # Add days
    for day in itinerary.get('days', []):
        html_content += f"""
        <div class="day">
            <h2>{day.get('title', f"Day {day.get('day', '')}")}</h2>
            <p>Date: {day.get('date', '')}</p>
        """
        
        for activity in day.get('activities', []):
            html_content += f"""
            <div class="activity">
                <h3>{activity.get('time', '')} - {activity.get('title', '')}</h3>
                <p>{activity.get('description', '')}</p>
                <p>Location: {activity.get('location', '')}</p>
                <p>Duration: {activity.get('duration', '')}</p>
                <p class="cost">Estimated Cost: ${activity.get('estimated_cost', 0)}</p>
            </div>
            """
        
        html_content += f"""
            <p><strong>Transportation:</strong> {day.get('transportation', {}).get('type', 'N/A')}</p>
            <p class="cost"><strong>Daily Total: ${day.get('total_estimated_cost', 0)}</strong></p>
            <p><em>Notes: {day.get('notes', '')}</em></p>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    return html_content

def share_itinerary(data: Dict[str, Any]) -> Dict[str, Any]:
    """Share itinerary with others"""
    
    try:
        user_id = data.get('user_id')
        share_method = data.get('method', 'link')  # 'link', 'email', 'export'
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        itinerary = dynamodb_client.get_itinerary(user_id)
        
        if not itinerary:
            return jsonify({'error': 'No itinerary found'}), 404
        
        if share_method == 'link':
            # Generate shareable link (simplified)
            share_id = f"share_{int(datetime.utcnow().timestamp())}"
            share_url = f"https://your-app-domain.com/shared/{share_id}"
            
            # Store shareable version
            shared_data = {
                'share_id': share_id,
                'itinerary': itinerary,
                'shared_by': user_id,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
            # In production, save this to a dedicated shares table
            
            return jsonify({
                'share_url': share_url,
                'share_id': share_id,
                'expires_in_days': 30
            })
        
        else:
            return jsonify({'error': 'Unsupported share method'}), 400
            
    except Exception as e:
        logging.error(f"Error sharing itinerary: {str(e)}")
        return jsonify({'error': 'Itinerary sharing error'}), 500