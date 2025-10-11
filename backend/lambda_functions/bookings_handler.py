import json
import logging
from datetime import datetime
from typing import Dict, Any
from flask import jsonify
from api_clients.flights_api import FlightsAPI
from api_clients.hotels_api import HotelsAPI
from dynamodb_client import DynamoDBClient
from s3_client import S3Client

# Initialize clients
flights_api = FlightsAPI()
hotels_api = HotelsAPI()
dynamodb_client = DynamoDBClient()
s3_client = S3Client()

def handle_booking(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle booking requests for flights, hotels, and other travel services"""
    
    try:
        user_id = data.get('user_id')
        booking_type = data.get('booking_type', '').lower()
        booking_details = data.get('booking_details', {})
        
        if not user_id or not booking_type:
            return jsonify({'error': 'Missing user_id or booking_type'}), 400
        
        # Route to appropriate booking handler
        if booking_type == 'flight':
            return handle_flight_booking(user_id, booking_details)
        elif booking_type == 'hotel':
            return handle_hotel_booking(user_id, booking_details)
        elif booking_type == 'car_rental':
            return handle_car_rental_booking(user_id, booking_details)
        else:
            return jsonify({'error': f'Unsupported booking type: {booking_type}'}), 400
            
    except Exception as e:
        logging.error(f"Error in handle_booking: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def handle_flight_booking(user_id: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
    """Handle flight booking requests"""
    
    try:
        # Extract flight search parameters
        origin = booking_details.get('origin')
        destination = booking_details.get('destination')
        departure_date = booking_details.get('departure_date')
        return_date = booking_details.get('return_date')
        passengers = booking_details.get('passengers', 1)
        cabin_class = booking_details.get('cabin_class', 'economy')
        
        # Validate required parameters
        if not all([origin, destination, departure_date]):
            return jsonify({
                'error': 'Missing required flight details',
                'required': ['origin', 'destination', 'departure_date']
            }), 400
        
        # Search for flights
        search_params = {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'return_date': return_date,
            'passengers': passengers,
            'cabin_class': cabin_class
        }
        
        flight_options = flights_api.search_flights(search_params)
        
        if not flight_options:
            return jsonify({
                'message': 'No flights found for your search criteria',
                'search_params': search_params
            })
        
        # Save search results to user's data
        search_data = {
            'type': 'flight_search',
            'search_params': search_params,
            'results': flight_options,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Get existing user data
        user_data = dynamodb_client.get_user_data(user_id) or {}
        searches = user_data.get('searches', [])
        searches.append(search_data)
        user_data['searches'] = searches[-10:]  # Keep only last 10 searches
        
        dynamodb_client.save_user_data(user_id, user_data)
        
        return jsonify({
            'message': f'Found {len(flight_options)} flight options',
            'flights': flight_options,
            'search_id': search_data['timestamp']
        })
        
    except Exception as e:
        logging.error(f"Error in handle_flight_booking: {str(e)}")
        return jsonify({'error': 'Flight booking service error'}), 500

def handle_hotel_booking(user_id: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
    """Handle hotel booking requests"""
    
    try:
        # Extract hotel search parameters
        location = booking_details.get('location')
        check_in = booking_details.get('check_in')
        check_out = booking_details.get('check_out')
        guests = booking_details.get('guests', 1)
        rooms = booking_details.get('rooms', 1)
        price_range = booking_details.get('price_range', {})
        
        # Validate required parameters
        if not all([location, check_in, check_out]):
            return jsonify({
                'error': 'Missing required hotel details',
                'required': ['location', 'check_in', 'check_out']
            }), 400
        
        # Search for hotels
        search_params = {
            'location': location,
            'check_in': check_in,
            'check_out': check_out,
            'guests': guests,
            'rooms': rooms,
            'price_range': price_range
        }
        
        hotel_options = hotels_api.search_hotels(search_params)
        
        if not hotel_options:
            return jsonify({
                'message': 'No hotels found for your search criteria',
                'search_params': search_params
            })
        
        # Save search results
        search_data = {
            'type': 'hotel_search',
            'search_params': search_params,
            'results': hotel_options,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Get existing user data
        user_data = dynamodb_client.get_user_data(user_id) or {}
        searches = user_data.get('searches', [])
        searches.append(search_data)
        user_data['searches'] = searches[-10:]
        
        dynamodb_client.save_user_data(user_id, user_data)
        
        return jsonify({
            'message': f'Found {len(hotel_options)} hotel options',
            'hotels': hotel_options,
            'search_id': search_data['timestamp']
        })
        
    except Exception as e:
        logging.error(f"Error in handle_hotel_booking: {str(e)}")
        return jsonify({'error': 'Hotel booking service error'}), 500

def handle_car_rental_booking(user_id: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
    """Handle car rental booking requests"""
    
    try:
        location = booking_details.get('location')
        pickup_date = booking_details.get('pickup_date')
        return_date = booking_details.get('return_date')
        
        if not all([location, pickup_date, return_date]):
            return jsonify({
                'error': 'Missing required car rental details',
                'required': ['location', 'pickup_date', 'return_date']
            }), 400
        
        # For now, return a mock response
        # In production, integrate with car rental APIs
        car_options = [
            {
                'id': 'car_001',
                'company': 'Enterprise',
                'car_type': 'Economy',
                'model': 'Toyota Corolla',
                'price_per_day': 35.00,
                'total_price': 105.00,
                'pickup_location': location,
                'features': ['Air Conditioning', 'Bluetooth', 'GPS']
            },
            {
                'id': 'car_002',
                'company': 'Hertz',
                'car_type': 'Mid-size',
                'model': 'Honda Accord',
                'price_per_day': 45.00,
                'total_price': 135.00,
                'pickup_location': location,
                'features': ['Air Conditioning', 'Bluetooth', 'GPS', 'Backup Camera']
            }
        ]
        
        return jsonify({
            'message': f'Found {len(car_options)} car rental options',
            'cars': car_options
        })
        
    except Exception as e:
        logging.error(f"Error in handle_car_rental_booking: {str(e)}")
        return jsonify({'error': 'Car rental service error'}), 500

def confirm_booking(data: Dict[str, Any]) -> Dict[str, Any]:
    """Confirm a booking selection"""
    
    try:
        user_id = data.get('user_id')
        booking_type = data.get('booking_type')
        selection = data.get('selection')
        payment_details = data.get('payment_details', {})
        
        if not all([user_id, booking_type, selection]):
            return jsonify({'error': 'Missing required confirmation details'}), 400
        
        # Create booking confirmation
        booking_confirmation = {
            'booking_id': f"{booking_type}_{int(datetime.utcnow().timestamp())}",
            'user_id': user_id,
            'type': booking_type,
            'details': selection,
            'payment_status': 'confirmed' if payment_details else 'pending',
            'booking_date': datetime.utcnow().isoformat(),
            'status': 'confirmed'
        }
        
        # Save booking to DynamoDB
        success = dynamodb_client.save_booking(user_id, booking_confirmation)
        
        if success:
            # Save booking confirmation to S3
            s3_key = s3_client.save_booking_confirmation(user_id, booking_confirmation)
            
            if s3_key:
                booking_confirmation['confirmation_document'] = s3_key
            
            return jsonify({
                'message': 'Booking confirmed successfully',
                'booking': booking_confirmation
            })
        else:
            return jsonify({'error': 'Failed to save booking'}), 500
            
    except Exception as e:
        logging.error(f"Error in confirm_booking: {str(e)}")
        return jsonify({'error': 'Booking confirmation error'}), 500

def get_user_bookings(user_id: str) -> Dict[str, Any]:
    """Get all bookings for a user"""
    
    try:
        bookings = dynamodb_client.get_bookings(user_id)
        
        return jsonify({
            'bookings': bookings,
            'count': len(bookings)
        })
        
    except Exception as e:
        logging.error(f"Error getting user bookings: {str(e)}")
        return jsonify({'error': 'Failed to retrieve bookings'}), 500

def cancel_booking(data: Dict[str, Any]) -> Dict[str, Any]:
    """Cancel a booking"""
    
    try:
        user_id = data.get('user_id')
        booking_id = data.get('booking_id')
        
        if not all([user_id, booking_id]):
            return jsonify({'error': 'Missing user_id or booking_id'}), 400
        
        # Get user bookings
        bookings = dynamodb_client.get_bookings(user_id)
        
        # Find and update the booking
        updated_bookings = []
        booking_found = False
        
        for booking in bookings:
            if booking.get('booking_id') == booking_id:
                booking['status'] = 'cancelled'
                booking['cancelled_at'] = datetime.utcnow().isoformat()
                booking_found = True
            updated_bookings.append(booking)
        
        if not booking_found:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Save updated bookings
        user_data = dynamodb_client.get_user_data(user_id) or {}
        user_data['bookings'] = updated_bookings
        
        success = dynamodb_client.save_user_data(user_id, user_data)
        
        if success:
            return jsonify({
                'message': 'Booking cancelled successfully',
                'booking_id': booking_id
            })
        else:
            return jsonify({'error': 'Failed to cancel booking'}), 500
            
    except Exception as e:
        logging.error(f"Error in cancel_booking: {str(e)}")
        return jsonify({'error': 'Booking cancellation error'}), 500