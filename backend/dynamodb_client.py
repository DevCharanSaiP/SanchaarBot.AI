import boto3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

class DynamoDBClient:
    """Client for managing DynamoDB operations"""
    
    def __init__(self):
        self.dynamodb = boto3.client('dynamodb')
        self.resource = boto3.resource('dynamodb')
        self.table_name = 'TravelItineraries'
        self.interactions_table = 'TravelInteractions'
        
    def save_user_data(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Save user data to DynamoDB"""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            item = {
                'UserID': {'S': user_id},
                'Data': {'S': json.dumps(data)},
                'UpdatedAt': {'S': timestamp},
                'TTL': {'N': str(int(datetime.utcnow().timestamp()) + 86400 * 365)}  # 1 year TTL
            }
            
            # Add specific fields based on data type
            if 'itinerary' in data:
                item['CurrentItinerary'] = {'S': json.dumps(data['itinerary'])}
            if 'preferences' in data:
                item['Preferences'] = {'S': json.dumps(data['preferences'])}
            if 'bookings' in data:
                item['Bookings'] = {'S': json.dumps(data['bookings'])}
                
            self.dynamodb.put_item(
                TableName=self.table_name,
                Item=item
            )
            
            return True
            
        except ClientError as e:
            logging.error(f"Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data from DynamoDB"""
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={'UserID': {'S': user_id}}
            )
            
            if 'Item' in response:
                item = response['Item']
                data = {
                    'user_id': user_id,
                    'updated_at': item.get('UpdatedAt', {}).get('S', ''),
                    'data': json.loads(item.get('Data', {}).get('S', '{}')),
                }
                
                # Add specific fields if they exist
                if 'CurrentItinerary' in item:
                    data['current_itinerary'] = json.loads(item['CurrentItinerary']['S'])
                if 'Preferences' in item:
                    data['preferences'] = json.loads(item['Preferences']['S'])
                if 'Bookings' in item:
                    data['bookings'] = json.loads(item['Bookings']['S'])
                    
                return data
                
            return None
            
        except ClientError as e:
            logging.error(f"Error getting user data: {e}")
            return None
    
    def save_itinerary(self, user_id: str, itinerary: Dict[str, Any]) -> bool:
        """Save user itinerary"""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'UserID': {'S': user_id}},
                UpdateExpression='SET CurrentItinerary = :itinerary, UpdatedAt = :timestamp',
                ExpressionAttributeValues={
                    ':itinerary': {'S': json.dumps(itinerary)},
                    ':timestamp': {'S': timestamp}
                },
                ReturnValues='UPDATED_NEW'
            )
            
            return True
            
        except ClientError as e:
            logging.error(f"Error saving itinerary: {e}")
            return False
    
    def get_itinerary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current itinerary"""
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={'UserID': {'S': user_id}},
                ProjectionExpression='CurrentItinerary'
            )
            
            if 'Item' in response and 'CurrentItinerary' in response['Item']:
                return json.loads(response['Item']['CurrentItinerary']['S'])
                
            return None
            
        except ClientError as e:
            logging.error(f"Error getting itinerary: {e}")
            return None
    
    def save_booking(self, user_id: str, booking: Dict[str, Any]) -> bool:
        """Save booking information"""
        try:
            timestamp = datetime.utcnow().isoformat()
            booking_id = f"booking_{int(datetime.utcnow().timestamp())}"
            
            # Get existing bookings
            existing_data = self.get_user_data(user_id)
            bookings = existing_data.get('bookings', []) if existing_data else []
            
            # Add new booking
            booking['booking_id'] = booking_id
            booking['created_at'] = timestamp
            bookings.append(booking)
            
            # Update user data
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'UserID': {'S': user_id}},
                UpdateExpression='SET Bookings = :bookings, UpdatedAt = :timestamp',
                ExpressionAttributeValues={
                    ':bookings': {'S': json.dumps(bookings)},
                    ':timestamp': {'S': timestamp}
                }
            )
            
            return True
            
        except ClientError as e:
            logging.error(f"Error saving booking: {e}")
            return False
    
    def get_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all bookings for a user"""
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={'UserID': {'S': user_id}},
                ProjectionExpression='Bookings'
            )
            
            if 'Item' in response and 'Bookings' in response['Item']:
                return json.loads(response['Item']['Bookings']['S'])
                
            return []
            
        except ClientError as e:
            logging.error(f"Error getting bookings: {e}")
            return []
    
    def save_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences"""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'UserID': {'S': user_id}},
                UpdateExpression='SET Preferences = :prefs, UpdatedAt = :timestamp',
                ExpressionAttributeValues={
                    ':prefs': {'S': json.dumps(preferences)},
                    ':timestamp': {'S': timestamp}
                }
            )
            
            return True
            
        except ClientError as e:
            logging.error(f"Error saving preferences: {e}")
            return False
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={'UserID': {'S': user_id}},
                ProjectionExpression='Preferences'
            )
            
            if 'Item' in response and 'Preferences' in response['Item']:
                return json.loads(response['Item']['Preferences']['S'])
                
            return {}
            
        except ClientError as e:
            logging.error(f"Error getting preferences: {e}")
            return {}
    
    def save_interaction(self, user_id: str, message: str, response: str, intent: str = None) -> bool:
        """Save user interaction"""
        try:
            timestamp = datetime.utcnow().isoformat()
            interaction_id = f"{user_id}#{timestamp}"
            
            item = {
                'InteractionID': {'S': interaction_id},
                'UserID': {'S': user_id},
                'Timestamp': {'S': timestamp},
                'UserMessage': {'S': message},
                'BotResponse': {'S': response},
                'TTL': {'N': str(int(datetime.utcnow().timestamp()) + 86400 * 30)}  # 30 days TTL
            }
            
            if intent:
                item['Intent'] = {'S': intent}
                
            self.dynamodb.put_item(
                TableName=self.interactions_table,
                Item=item
            )
            
            return True
            
        except ClientError as e:
            logging.error(f"Error saving interaction: {e}")
            return False
    
    def get_user_interactions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent user interactions"""
        try:
            response = self.dynamodb.query(
                TableName=self.interactions_table,
                IndexName='UserID-Timestamp-index',  # Assumes GSI exists
                KeyConditionExpression='UserID = :user_id',
                ExpressionAttributeValues={
                    ':user_id': {'S': user_id}
                },
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            interactions = []
            for item in response.get('Items', []):
                interactions.append({
                    'timestamp': item['Timestamp']['S'],
                    'user_message': item['UserMessage']['S'],
                    'bot_response': item['BotResponse']['S'],
                    'intent': item.get('Intent', {}).get('S', '')
                })
                
            return interactions
            
        except ClientError as e:
            logging.error(f"Error getting interactions: {e}")
            return []
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data"""
        try:
            # Delete main user record
            self.dynamodb.delete_item(
                TableName=self.table_name,
                Key={'UserID': {'S': user_id}}
            )
            
            # Note: In production, you might want to also clean up interactions
            # This is a simplified version
            
            return True
            
        except ClientError as e:
            logging.error(f"Error deleting user data: {e}")
            return False
    
    def create_tables_if_not_exist(self):
        """Create DynamoDB tables if they don't exist"""
        try:
            # Create main table
            try:
                self.dynamodb.describe_table(TableName=self.table_name)
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    self.dynamodb.create_table(
                        TableName=self.table_name,
                        KeySchema=[
                            {'AttributeName': 'UserID', 'KeyType': 'HASH'}
                        ],
                        AttributeDefinitions=[
                            {'AttributeName': 'UserID', 'AttributeType': 'S'}
                        ],
                        BillingMode='PAY_PER_REQUEST'
                    )
                    
            # Create interactions table
            try:
                self.dynamodb.describe_table(TableName=self.interactions_table)
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    self.dynamodb.create_table(
                        TableName=self.interactions_table,
                        KeySchema=[
                            {'AttributeName': 'InteractionID', 'KeyType': 'HASH'}
                        ],
                        AttributeDefinitions=[
                            {'AttributeName': 'InteractionID', 'AttributeType': 'S'},
                            {'AttributeName': 'UserID', 'AttributeType': 'S'},
                            {'AttributeName': 'Timestamp', 'AttributeType': 'S'}
                        ],
                        GlobalSecondaryIndexes=[
                            {
                                'IndexName': 'UserID-Timestamp-index',
                                'KeySchema': [
                                    {'AttributeName': 'UserID', 'KeyType': 'HASH'},
                                    {'AttributeName': 'Timestamp', 'KeyType': 'RANGE'}
                                ],
                                'Projection': {'ProjectionType': 'ALL'}
                            }
                        ],
                        BillingMode='PAY_PER_REQUEST'
                    )
                    
            return True
            
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
            return False