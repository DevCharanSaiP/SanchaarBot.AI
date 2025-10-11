import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from flask import jsonify
from api_clients.weather_api import WeatherAPI
from api_clients.news_api import NewsAPI
from dynamodb_client import DynamoDBClient
import boto3

# Initialize clients
weather_api = WeatherAPI()
news_api = NewsAPI()
dynamodb_client = DynamoDBClient()
sns_client = boto3.client('sns')

def handle_alerts(user_id: str) -> Dict[str, Any]:
    """Handle travel alerts for a specific user"""
    
    try:
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        # Get user's current bookings and itineraries
        user_data = dynamodb_client.get_user_data(user_id)
        if not user_data:
            return jsonify({
                'message': 'No user data found',
                'alerts': []
            })
        
        alerts = []
        
        # Check flight alerts
        flight_alerts = check_flight_alerts(user_data.get('bookings', []))
        alerts.extend(flight_alerts)
        
        # Check weather alerts
        weather_alerts = check_weather_alerts(user_data.get('current_itinerary', {}))
        alerts.extend(weather_alerts)
        
        # Check news/travel advisory alerts
        news_alerts = check_news_alerts(user_data.get('current_itinerary', {}))
        alerts.extend(news_alerts)
        
        # Check document expiry alerts
        document_alerts = check_document_alerts(user_id)
        alerts.extend(document_alerts)
        
        # Sort alerts by priority
        alerts.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        # Save alerts to user data
        user_data['last_alert_check'] = datetime.utcnow().isoformat()
        user_data['current_alerts'] = alerts
        dynamodb_client.save_user_data(user_id, user_data)
        
        return jsonify({
            'alerts': alerts,
            'count': len(alerts),
            'last_updated': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error in handle_alerts: {str(e)}")
        return jsonify({'error': 'Alert service error'}), 500

def check_flight_alerts(bookings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for flight-related alerts"""
    
    alerts = []
    
    try:
        for booking in bookings:
            if booking.get('type') != 'flight' or booking.get('status') != 'confirmed':
                continue
            
            flight_details = booking.get('details', {})
            departure_date = flight_details.get('departure_date')
            
            if not departure_date:
                continue
            
            # Parse departure date
            try:
                dept_datetime = datetime.fromisoformat(departure_date.replace('Z', '+00:00'))
            except:
                continue
            
            now = datetime.utcnow()
            time_diff = dept_datetime - now
            
            # Check for check-in reminders
            if timedelta(hours=22) <= time_diff <= timedelta(hours=24):
                alerts.append({
                    'type': 'flight_checkin_reminder',
                    'priority': 3,
                    'title': 'Flight Check-in Available',
                    'message': f"Check-in is now available for your flight {flight_details.get('flight_number', 'N/A')}",
                    'booking_id': booking.get('booking_id'),
                    'action_required': True,
                    'created_at': now.isoformat()
                })
            
            # Check for departure reminders
            elif timedelta(hours=2) <= time_diff <= timedelta(hours=3):
                alerts.append({
                    'type': 'departure_reminder',
                    'priority': 4,
                    'title': 'Upcoming Flight Departure',
                    'message': f"Your flight {flight_details.get('flight_number', 'N/A')} departs in approximately {time_diff.total_seconds() / 3600:.1f} hours",
                    'booking_id': booking.get('booking_id'),
                    'action_required': False,
                    'created_at': now.isoformat()
                })
            
            # Check for gate changes (simulated - in production, integrate with airline APIs)
            # This would typically come from real-time flight status APIs
            if time_diff <= timedelta(hours=6) and time_diff >= timedelta(hours=0):
                # Simulate occasional gate changes
                import random
                if random.random() < 0.1:  # 10% chance of gate change
                    alerts.append({
                        'type': 'gate_change',
                        'priority': 5,
                        'title': 'Gate Change Alert',
                        'message': f"Gate change for flight {flight_details.get('flight_number', 'N/A')}. New gate: {random.choice(['A12', 'B23', 'C34', 'D45'])}",
                        'booking_id': booking.get('booking_id'),
                        'action_required': True,
                        'created_at': now.isoformat()
                    })
    
    except Exception as e:
        logging.error(f"Error checking flight alerts: {str(e)}")
    
    return alerts

def check_weather_alerts(itinerary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for weather-related alerts"""
    
    alerts = []
    
    try:
        destinations = itinerary.get('destinations', [])
        
        for destination in destinations:
            location = destination.get('location')
            arrival_date = destination.get('arrival_date')
            
            if not location or not arrival_date:
                continue
            
            # Get weather forecast
            weather_data = weather_api.get_forecast(location)
            
            if not weather_data:
                continue
            
            # Check for severe weather
            for day_forecast in weather_data.get('forecast', []):
                forecast_date = day_forecast.get('date')
                conditions = day_forecast.get('conditions', {})
                
                # Check for severe weather conditions
                if any(condition in conditions.get('description', '').lower() 
                       for condition in ['storm', 'hurricane', 'blizzard', 'flood']):
                    alerts.append({
                        'type': 'severe_weather',
                        'priority': 4,
                        'title': f'Severe Weather Alert - {location}',
                        'message': f"Severe weather expected in {location} on {forecast_date}: {conditions.get('description', 'N/A')}",
                        'location': location,
                        'date': forecast_date,
                        'action_required': True,
                        'created_at': datetime.utcnow().isoformat()
                    })
                
                # Check for travel disruptions
                elif any(condition in conditions.get('description', '').lower() 
                        for condition in ['heavy rain', 'heavy snow', 'fog']):
                    alerts.append({
                        'type': 'weather_advisory',
                        'priority': 2,
                        'title': f'Weather Advisory - {location}',
                        'message': f"Weather conditions may affect travel in {location} on {forecast_date}: {conditions.get('description', 'N/A')}",
                        'location': location,
                        'date': forecast_date,
                        'action_required': False,
                        'created_at': datetime.utcnow().isoformat()
                    })
    
    except Exception as e:
        logging.error(f"Error checking weather alerts: {str(e)}")
    
    return alerts

def check_news_alerts(itinerary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for news and travel advisory alerts"""
    
    alerts = []
    
    try:
        destinations = itinerary.get('destinations', [])
        
        for destination in destinations:
            location = destination.get('location')
            country = destination.get('country', location)
            
            if not location:
                continue
            
            # Get news for the destination
            news_data = news_api.get_travel_news(country)
            
            if not news_data:
                continue
            
            # Check for travel advisories
            for article in news_data.get('articles', [])[:3]:  # Check top 3 articles
                title = article.get('title', '')
                description = article.get('description', '')
                
                # Look for travel-related keywords
                travel_keywords = [
                    'travel advisory', 'border closure', 'flight cancellation',
                    'embassy', 'security alert', 'strike', 'protest',
                    'visa requirement', 'entry restriction'
                ]
                
                if any(keyword in title.lower() or keyword in description.lower() 
                       for keyword in travel_keywords):
                    alerts.append({
                        'type': 'travel_advisory',
                        'priority': 3,
                        'title': f'Travel Advisory - {country}',
                        'message': f"Travel news for {country}: {title[:100]}...",
                        'location': location,
                        'country': country,
                        'source': article.get('source', 'Unknown'),
                        'url': article.get('url', ''),
                        'action_required': True,
                        'created_at': datetime.utcnow().isoformat()
                    })
    
    except Exception as e:
        logging.error(f"Error checking news alerts: {str(e)}")
    
    return alerts

def check_document_alerts(user_id: str) -> List[Dict[str, Any]]:
    """Check for document expiry and requirement alerts"""
    
    alerts = []
    
    try:
        from s3_client import S3Client
        s3_client = S3Client()
        
        # Get user documents
        documents = s3_client.list_user_documents(user_id)
        
        for doc in documents:
            doc_type = doc.get('document_type', '')
            
            # Check for passport expiry (simulated)
            if doc_type == 'identification' and 'passport' in doc.get('filename', '').lower():
                # In production, you would parse the document to get actual expiry date
                # For demo, we'll simulate some passport expiring soon
                import random
                if random.random() < 0.2:  # 20% chance of passport expiring soon
                    alerts.append({
                        'type': 'document_expiry',
                        'priority': 4,
                        'title': 'Passport Expiry Warning',
                        'message': 'Your passport may expire soon. Please verify the expiry date and renew if necessary.',
                        'document': doc.get('filename'),
                        'action_required': True,
                        'created_at': datetime.utcnow().isoformat()
                    })
    
    except Exception as e:
        logging.error(f"Error checking document alerts: {str(e)}")
    
    return alerts

def send_alert_notification(user_id: str, alert: Dict[str, Any]) -> bool:
    """Send alert notification via SNS"""
    
    try:
        # Get user preferences for notifications
        user_data = dynamodb_client.get_user_data(user_id)
        preferences = user_data.get('preferences', {}) if user_data else {}
        
        notification_settings = preferences.get('notifications', {})
        
        # Check if user wants this type of notification
        alert_type = alert.get('type', '')
        if not notification_settings.get(alert_type, True):  # Default to True
            return True
        
        # Create SNS message
        message = {
            'default': alert.get('message', ''),
            'email': f"Travel Alert: {alert.get('title', '')}\n\n{alert.get('message', '')}",
            'sms': alert.get('title', '')[:160]  # SMS character limit
        }
        
        # Publish to SNS topic (assumes topic exists)
        topic_arn = f"arn:aws:sns:{boto3.Session().region_name}:{boto3.client('sts').get_caller_identity()['Account']}:travel-alerts-{user_id}"
        
        sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            MessageStructure='json',
            Subject=alert.get('title', 'Travel Alert')
        )
        
        return True
        
    except Exception as e:
        logging.error(f"Error sending alert notification: {str(e)}")
        return False

def create_custom_alert(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a custom user alert"""
    
    try:
        user_id = data.get('user_id')
        alert_data = data.get('alert', {})
        
        if not user_id or not alert_data:
            return jsonify({'error': 'Missing user_id or alert data'}), 400
        
        # Create custom alert
        custom_alert = {
            'type': 'custom',
            'priority': alert_data.get('priority', 1),
            'title': alert_data.get('title', 'Custom Alert'),
            'message': alert_data.get('message', ''),
            'trigger_date': alert_data.get('trigger_date'),
            'action_required': alert_data.get('action_required', False),
            'created_at': datetime.utcnow().isoformat(),
            'user_created': True
        }
        
        # Save to user data
        user_data = dynamodb_client.get_user_data(user_id) or {}
        custom_alerts = user_data.get('custom_alerts', [])
        custom_alerts.append(custom_alert)
        user_data['custom_alerts'] = custom_alerts
        
        success = dynamodb_client.save_user_data(user_id, user_data)
        
        if success:
            return jsonify({
                'message': 'Custom alert created successfully',
                'alert': custom_alert
            })
        else:
            return jsonify({'error': 'Failed to create alert'}), 500
            
    except Exception as e:
        logging.error(f"Error creating custom alert: {str(e)}")
        return jsonify({'error': 'Custom alert creation error'}), 500

def dismiss_alert(data: Dict[str, Any]) -> Dict[str, Any]:
    """Dismiss/mark alert as read"""
    
    try:
        user_id = data.get('user_id')
        alert_id = data.get('alert_id')
        
        if not user_id or not alert_id:
            return jsonify({'error': 'Missing user_id or alert_id'}), 400
        
        # Get user data
        user_data = dynamodb_client.get_user_data(user_id)
        if not user_data:
            return jsonify({'error': 'User data not found'}), 404
        
        # Mark alert as dismissed
        dismissed_alerts = user_data.get('dismissed_alerts', [])
        dismissed_alerts.append({
            'alert_id': alert_id,
            'dismissed_at': datetime.utcnow().isoformat()
        })
        
        user_data['dismissed_alerts'] = dismissed_alerts
        
        success = dynamodb_client.save_user_data(user_id, user_data)
        
        if success:
            return jsonify({'message': 'Alert dismissed successfully'})
        else:
            return jsonify({'error': 'Failed to dismiss alert'}), 500
            
    except Exception as e:
        logging.error(f"Error dismissing alert: {str(e)}")
        return jsonify({'error': 'Alert dismissal error'}), 500