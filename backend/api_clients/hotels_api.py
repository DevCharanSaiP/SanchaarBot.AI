import requests
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
import random

class HotelsAPI:
    """Client for hotel booking and search APIs"""
    
    def __init__(self):
        # Booking.com API credentials
        self.booking_api_key = os.environ.get('BOOKING_API_KEY')
        self.booking_base_url = 'https://distribution-xml.booking.com/json/bookings'
        
        # Expedia Rapid API credentials
        self.expedia_api_key = os.environ.get('EXPEDIA_API_KEY')
        self.expedia_secret = os.environ.get('EXPEDIA_SECRET')
        self.expedia_base_url = 'https://test.ean.com/ean-services'
        
        # Hotels.com API
        self.hotels_api_key = os.environ.get('HOTELS_API_KEY')
        
    def search_hotels(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for hotels"""
        
        try:
            # Try Booking.com API first
            if self.booking_api_key:
                hotels = self._search_booking_com(search_params)
                if hotels:
                    return hotels
            
            # Fallback to mock data
            return self._get_mock_hotel_data(search_params)
            
        except Exception as e:
            logging.error(f"Error searching hotels: {str(e)}")
            return self._get_mock_hotel_data(search_params)
    
    def _search_booking_com(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search hotels using Booking.com API"""
        
        try:
            url = f"{self.booking_base_url}/getHotels.json"
            
            headers = {
                'User-Agent': 'Travel Companion Agent/1.0',
                'Content-Type': 'application/json'
            }
            
            # Convert search parameters to Booking.com format
            booking_params = {
                'city': search_params.get('location'),
                'checkin': search_params.get('check_in'),
                'checkout': search_params.get('check_out'),
                'adults': search_params.get('guests', 1),
                'rooms': search_params.get('rooms', 1),
                'currency': 'USD',
                'language': 'en'
            }
            
            response = requests.get(url, headers=headers, params=booking_params)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_booking_response(data)
            else:
                return []
                
        except Exception as e:
            logging.error(f"Error with Booking.com API: {str(e)}")
            return []
    
    def _parse_booking_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Booking.com API response"""
        
        hotels = []
        
        try:
            hotel_data = data.get('result', [])
            
            for hotel in hotel_data:
                parsed_hotel = {
                    'id': hotel.get('hotel_id'),
                    'name': hotel.get('hotel_name', 'Unknown Hotel'),
                    'address': hotel.get('address', ''),
                    'city': hotel.get('city', ''),
                    'country': hotel.get('country_trans', ''),
                    'star_rating': hotel.get('class', 0),
                    'price': {
                        'total': float(hotel.get('min_total_price', 0)),
                        'currency': hotel.get('currency_code', 'USD'),
                        'per_night': float(hotel.get('price', 0))
                    },
                    'amenities': hotel.get('hotel_facilities', []),
                    'description': hotel.get('hotel_description', ''),
                    'images': hotel.get('photo_urls', []),
                    'rating': {
                        'score': float(hotel.get('review_score', 0)),
                        'count': int(hotel.get('review_nr', 0))
                    },
                    'coordinates': {
                        'latitude': float(hotel.get('latitude', 0)),
                        'longitude': float(hotel.get('longitude', 0))
                    }
                }
                
                hotels.append(parsed_hotel)
                
            return hotels
            
        except Exception as e:
            logging.error(f"Error parsing Booking.com response: {str(e)}")
            return []
    
    def _get_mock_hotel_data(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return mock hotel data for testing"""
        
        location = search_params.get('location', 'New York')
        check_in = search_params.get('check_in', datetime.utcnow().strftime('%Y-%m-%d'))
        
        mock_hotels = [
            {
                'id': 'hotel_001',
                'name': f'Grand {location} Hotel',
                'address': f'123 Main Street, {location}',
                'city': location,
                'country': 'United States',
                'star_rating': 4,
                'price': {
                    'total': 180.00,
                    'currency': 'USD',
                    'per_night': 180.00
                },
                'amenities': [
                    'Free WiFi', 'Fitness Center', 'Restaurant', 
                    'Room Service', 'Concierge', 'Business Center'
                ],
                'description': f'Luxury hotel in the heart of {location} with modern amenities and excellent service.',
                'images': [
                    'https://example.com/hotel1_image1.jpg',
                    'https://example.com/hotel1_image2.jpg'
                ],
                'rating': {
                    'score': 8.5,
                    'count': 1250
                },
                'coordinates': {
                    'latitude': 40.7128,
                    'longitude': -74.0060
                }
            },
            {
                'id': 'hotel_002',
                'name': f'{location} Business Suites',
                'address': f'456 Business Ave, {location}',
                'city': location,
                'country': 'United States',
                'star_rating': 3,
                'price': {
                    'total': 120.00,
                    'currency': 'USD',
                    'per_night': 120.00
                },
                'amenities': [
                    'Free WiFi', 'Business Center', 'Parking', 
                    'Breakfast Included', 'Airport Shuttle'
                ],
                'description': f'Comfortable business hotel perfect for travelers visiting {location}.',
                'images': [
                    'https://example.com/hotel2_image1.jpg'
                ],
                'rating': {
                    'score': 7.8,
                    'count': 856
                },
                'coordinates': {
                    'latitude': 40.7580,
                    'longitude': -73.9855
                }
            },
            {
                'id': 'hotel_003',
                'name': f'Budget Inn {location}',
                'address': f'789 Economy St, {location}',
                'city': location,
                'country': 'United States',
                'star_rating': 2,
                'price': {
                    'total': 75.00,
                    'currency': 'USD',
                    'per_night': 75.00
                },
                'amenities': [
                    'Free WiFi', 'Parking', '24-hour Front Desk'
                ],
                'description': f'Budget-friendly accommodation in {location} with essential amenities.',
                'images': [
                    'https://example.com/hotel3_image1.jpg'
                ],
                'rating': {
                    'score': 6.9,
                    'count': 432
                },
                'coordinates': {
                    'latitude': 40.6892,
                    'longitude': -74.0445
                }
            }
        ]
        
        return mock_hotels
    
    def get_hotel_details(self, hotel_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific hotel"""
        
        try:
            # In a real implementation, this would fetch detailed hotel info
            # For now, return mock detailed data
            
            detailed_info = {
                'id': hotel_id,
                'name': 'Grand Plaza Hotel',
                'address': '123 Main Street, New York, NY 10001',
                'description': 'Luxury hotel in the heart of Manhattan with stunning city views.',
                'star_rating': 4,
                'check_in_time': '15:00',
                'check_out_time': '11:00',
                'amenities': [
                    'Free WiFi', 'Fitness Center', 'Restaurant', 'Room Service',
                    'Concierge', 'Business Center', 'Spa', 'Pool', 'Parking'
                ],
                'room_types': [
                    {
                        'type': 'Standard Room',
                        'description': 'Comfortable room with city view',
                        'capacity': 2,
                        'price_per_night': 180.00,
                        'amenities': ['Free WiFi', 'Air Conditioning', 'TV', 'Mini Bar']
                    },
                    {
                        'type': 'Deluxe Suite',
                        'description': 'Spacious suite with separate living area',
                        'capacity': 4,
                        'price_per_night': 320.00,
                        'amenities': ['Free WiFi', 'Air Conditioning', 'TV', 'Mini Bar', 'Kitchenette']
                    }
                ],
                'policies': {
                    'cancellation': 'Free cancellation up to 24 hours before check-in',
                    'pets': 'Pets allowed with additional fee',
                    'smoking': 'Non-smoking property'
                },
                'contact': {
                    'phone': '+1-212-555-0123',
                    'email': 'info@grandplaza.com',
                    'website': 'https://grandplaza.com'
                },
                'coordinates': {
                    'latitude': 40.7128,
                    'longitude': -74.0060
                }
            }
            
            return detailed_info
            
        except Exception as e:
            logging.error(f"Error getting hotel details: {str(e)}")
            return None
    
    def book_hotel(self, hotel_id: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Book a hotel room"""
        
        try:
            # In a real implementation, this would handle payment and booking
            # For now, return a mock booking confirmation
            
            booking_confirmation = {
                'booking_id': f"HTL{int(datetime.utcnow().timestamp())}",
                'hotel_id': hotel_id,
                'status': 'confirmed',
                'confirmation_code': f"CONF{random.randint(100000, 999999)}",
                'guest_details': booking_details.get('guest_details', {}),
                'room_details': booking_details.get('room_details', {}),
                'check_in_date': booking_details.get('check_in'),
                'check_out_date': booking_details.get('check_out'),
                'total_nights': self._calculate_nights(
                    booking_details.get('check_in'),
                    booking_details.get('check_out')
                ),
                'total_price': booking_details.get('total_price', 360.00),
                'currency': 'USD',
                'booking_date': datetime.utcnow().isoformat(),
                'payment_status': 'confirmed'
            }
            
            return booking_confirmation
            
        except Exception as e:
            logging.error(f"Error booking hotel: {str(e)}")
            return {'error': 'Booking failed'}
    
    def cancel_hotel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel a hotel booking"""
        
        try:
            # In a real implementation, this would handle cancellation policies
            
            return {
                'booking_id': booking_id,
                'status': 'cancelled',
                'cancelled_at': datetime.utcnow().isoformat(),
                'refund_amount': 300.00,  # Example refund after fees
                'refund_status': 'processing',
                'cancellation_fee': 60.00
            }
            
        except Exception as e:
            logging.error(f"Error cancelling hotel booking: {str(e)}")
            return {'error': 'Cancellation failed'}
    
    def get_hotel_availability(self, hotel_id: str, check_in: str, check_out: str) -> Dict[str, Any]:
        """Check hotel availability for specific dates"""
        
        try:
            # Mock availability data
            availability = {
                'hotel_id': hotel_id,
                'check_in_date': check_in,
                'check_out_date': check_out,
                'available': True,
                'rooms_available': [
                    {
                        'room_type': 'Standard Room',
                        'available_rooms': 5,
                        'price_per_night': 180.00,
                        'total_price': self._calculate_total_price(check_in, check_out, 180.00)
                    },
                    {
                        'room_type': 'Deluxe Suite',
                        'available_rooms': 2,
                        'price_per_night': 320.00,
                        'total_price': self._calculate_total_price(check_in, check_out, 320.00)
                    }
                ],
                'restrictions': [
                    'Minimum stay: 1 night',
                    'Maximum stay: 14 nights'
                ]
            }
            
            return availability
            
        except Exception as e:
            logging.error(f"Error checking hotel availability: {str(e)}")
            return {'available': False, 'error': 'Availability check failed'}
    
    def search_hotels_by_location(self, latitude: float, longitude: float, 
                                radius_km: int = 5) -> List[Dict[str, Any]]:
        """Search for hotels near specific coordinates"""
        
        try:
            # Mock location-based search
            nearby_hotels = [
                {
                    'id': 'hotel_nearby_001',
                    'name': 'Downtown City Hotel',
                    'distance_km': 0.8,
                    'price': {'per_night': 160.00, 'currency': 'USD'},
                    'rating': {'score': 8.2, 'count': 945},
                    'coordinates': {
                        'latitude': latitude + 0.005,
                        'longitude': longitude + 0.005
                    }
                },
                {
                    'id': 'hotel_nearby_002',
                    'name': 'Riverside Inn',
                    'distance_km': 2.3,
                    'price': {'per_night': 95.00, 'currency': 'USD'},
                    'rating': {'score': 7.6, 'count': 512},
                    'coordinates': {
                        'latitude': latitude - 0.015,
                        'longitude': longitude + 0.020
                    }
                }
            ]
            
            return nearby_hotels
            
        except Exception as e:
            logging.error(f"Error searching hotels by location: {str(e)}")
            return []
    
    def get_hotel_reviews(self, hotel_id: str) -> List[Dict[str, Any]]:
        """Get recent reviews for a hotel"""
        
        try:
            # Mock review data
            reviews = [
                {
                    'id': 'review_001',
                    'guest_name': 'John D.',
                    'rating': 9,
                    'title': 'Excellent stay!',
                    'comment': 'Great location, clean rooms, friendly staff. Would definitely stay again.',
                    'date': '2024-01-10',
                    'verified_stay': True
                },
                {
                    'id': 'review_002',
                    'guest_name': 'Sarah M.',
                    'rating': 8,
                    'title': 'Good value for money',
                    'comment': 'Nice hotel with good amenities. Breakfast could be better.',
                    'date': '2024-01-08',
                    'verified_stay': True
                },
                {
                    'id': 'review_003',
                    'guest_name': 'Mike R.',
                    'rating': 7,
                    'title': 'Decent hotel',
                    'comment': 'Average hotel, nothing special but clean and comfortable.',
                    'date': '2024-01-05',
                    'verified_stay': True
                }
            ]
            
            return reviews
            
        except Exception as e:
            logging.error(f"Error getting hotel reviews: {str(e)}")
            return []
    
    def _calculate_nights(self, check_in: str, check_out: str) -> int:
        """Calculate number of nights between check-in and check-out"""
        
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
            return (check_out_date - check_in_date).days
        except:
            return 1
    
    def _calculate_total_price(self, check_in: str, check_out: str, price_per_night: float) -> float:
        """Calculate total price for stay"""
        
        nights = self._calculate_nights(check_in, check_out)
        return nights * price_per_night