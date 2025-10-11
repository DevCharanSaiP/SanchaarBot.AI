import requests
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os

class FlightsAPI:
    """Client for flight booking and search APIs"""
    
    def __init__(self):
        # Amadeus API credentials (add your credentials)
        self.amadeus_api_key = os.environ.get('AMADEUS_API_KEY')
        self.amadeus_secret = os.environ.get('AMADEUS_SECRET')
        self.amadeus_base_url = 'https://api.amadeus.com/v2'
        
        # Alternative: Skyscanner API
        self.skyscanner_api_key = os.environ.get('SKYSCANNER_API_KEY')
        self.skyscanner_base_url = 'https://partners.api.skyscanner.net/apiservices'
        
        self.access_token = None
        self.token_expires = None
        
    def _get_amadeus_token(self) -> bool:
        """Get Amadeus API access token"""
        
        try:
            if self.access_token and self.token_expires and datetime.utcnow() < self.token_expires:
                return True
                
            url = "https://api.amadeus.com/v1/security/oauth2/token"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.amadeus_api_key,
                'client_secret': self.amadeus_secret
            }
            
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires = datetime.utcnow() + timedelta(seconds=expires_in - 60)
            
            return True
            
        except Exception as e:
            logging.error(f"Error getting Amadeus token: {str(e)}")
            return False
    
    def search_flights(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for flights using Amadeus API"""
        
        try:
            if not self._get_amadeus_token():
                return self._get_mock_flight_data(search_params)
            
            url = f"{self.amadeus_base_url}/shopping/flight-offers"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Convert search parameters to Amadeus format
            amadeus_params = {
                'originLocationCode': search_params.get('origin'),
                'destinationLocationCode': search_params.get('destination'),
                'departureDate': search_params.get('departure_date'),
                'adults': search_params.get('passengers', 1),
                'currencyCode': 'USD',
                'max': 10
            }
            
            if search_params.get('return_date'):
                amadeus_params['returnDate'] = search_params['return_date']
            
            if search_params.get('cabin_class'):
                class_mapping = {
                    'economy': 'ECONOMY',
                    'premium_economy': 'PREMIUM_ECONOMY',
                    'business': 'BUSINESS',
                    'first': 'FIRST'
                }
                amadeus_params['travelClass'] = class_mapping.get(search_params['cabin_class'], 'ECONOMY')
            
            response = requests.get(url, headers=headers, params=amadeus_params)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_amadeus_response(data)
            else:
                logging.warning(f"Amadeus API error: {response.status_code}")
                return self._get_mock_flight_data(search_params)
                
        except Exception as e:
            logging.error(f"Error searching flights: {str(e)}")
            return self._get_mock_flight_data(search_params)
    
    def _parse_amadeus_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Amadeus API response to standard format"""
        
        flights = []
        
        try:
            flight_offers = data.get('data', [])
            
            for offer in flight_offers:
                itineraries = offer.get('itineraries', [])
                price = offer.get('price', {})
                
                for itinerary in itineraries:
                    segments = itinerary.get('segments', [])
                    
                    if segments:
                        first_segment = segments[0]
                        last_segment = segments[-1]
                        
                        flight = {
                            'id': offer.get('id'),
                            'airline': first_segment.get('carrierCode', 'Unknown'),
                            'flight_number': f"{first_segment.get('carrierCode', '')}{first_segment.get('number', '')}",
                            'origin': first_segment.get('departure', {}).get('iataCode', ''),
                            'destination': last_segment.get('arrival', {}).get('iataCode', ''),
                            'departure_time': first_segment.get('departure', {}).get('at', ''),
                            'arrival_time': last_segment.get('arrival', {}).get('at', ''),
                            'duration': itinerary.get('duration', ''),
                            'stops': len(segments) - 1,
                            'price': {
                                'total': float(price.get('total', 0)),
                                'currency': price.get('currency', 'USD'),
                                'base': float(price.get('base', 0))
                            },
                            'cabin_class': segments[0].get('cabin', ''),
                            'aircraft': segments[0].get('aircraft', {}).get('code', ''),
                            'booking_class': segments[0].get('bookingClass', '')
                        }
                        
                        flights.append(flight)
            
            return flights
            
        except Exception as e:
            logging.error(f"Error parsing Amadeus response: {str(e)}")
            return []
    
    def _get_mock_flight_data(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return mock flight data for testing"""
        
        origin = search_params.get('origin', 'JFK')
        destination = search_params.get('destination', 'LAX')
        departure_date = search_params.get('departure_date', datetime.utcnow().strftime('%Y-%m-%d'))
        
        mock_flights = [
            {
                'id': 'mock_flight_001',
                'airline': 'AA',
                'flight_number': 'AA123',
                'origin': origin,
                'destination': destination,
                'departure_time': f'{departure_date}T08:00:00',
                'arrival_time': f'{departure_date}T11:30:00',
                'duration': 'PT5H30M',
                'stops': 0,
                'price': {
                    'total': 299.99,
                    'currency': 'USD',
                    'base': 250.00
                },
                'cabin_class': 'Economy',
                'aircraft': 'A320',
                'booking_class': 'Y'
            },
            {
                'id': 'mock_flight_002',
                'airline': 'DL',
                'flight_number': 'DL456',
                'origin': origin,
                'destination': destination,
                'departure_time': f'{departure_date}T14:30:00',
                'arrival_time': f'{departure_date}T18:15:00',
                'duration': 'PT5H45M',
                'stops': 1,
                'price': {
                    'total': 279.99,
                    'currency': 'USD',
                    'base': 230.00
                },
                'cabin_class': 'Economy',
                'aircraft': 'B737',
                'booking_class': 'Y'
            },
            {
                'id': 'mock_flight_003',
                'airline': 'UA',
                'flight_number': 'UA789',
                'origin': origin,
                'destination': destination,
                'departure_time': f'{departure_date}T19:45:00',
                'arrival_time': f'{departure_date}T23:20:00',
                'duration': 'PT5H35M',
                'stops': 0,
                'price': {
                    'total': 349.99,
                    'currency': 'USD',
                    'base': 300.00
                },
                'cabin_class': 'Economy',
                'aircraft': 'B777',
                'booking_class': 'Y'
            }
        ]
        
        return mock_flights
    
    def get_flight_status(self, flight_number: str, departure_date: str) -> Optional[Dict[str, Any]]:
        """Get real-time flight status"""
        
        try:
            if not self._get_amadeus_token():
                return self._get_mock_flight_status(flight_number)
            
            url = f"{self.amadeus_base_url}/schedule/flights"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'carrierCode': flight_number[:2],
                'flightNumber': flight_number[2:],
                'scheduledDepartureDate': departure_date
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_flight_status_response(data)
            else:
                return self._get_mock_flight_status(flight_number)
                
        except Exception as e:
            logging.error(f"Error getting flight status: {str(e)}")
            return self._get_mock_flight_status(flight_number)
    
    def _get_mock_flight_status(self, flight_number: str) -> Dict[str, Any]:
        """Return mock flight status"""
        
        import random
        
        statuses = ['On Time', 'Delayed', 'Boarding', 'Departed', 'Arrived']
        
        return {
            'flight_number': flight_number,
            'status': random.choice(statuses),
            'departure_time': '2024-01-15T08:00:00',
            'arrival_time': '2024-01-15T11:30:00',
            'gate': f'A{random.randint(1, 50)}',
            'terminal': random.choice(['1', '2', '3', '4']),
            'delay_minutes': random.randint(0, 60) if random.random() < 0.3 else 0
        }
    
    def book_flight(self, flight_id: str, passenger_details: Dict[str, Any]) -> Dict[str, Any]:
        """Book a flight (simplified booking process)"""
        
        try:
            # In a real implementation, this would handle payment and booking
            # For now, return a mock booking confirmation
            
            booking_confirmation = {
                'booking_id': f"BK{int(datetime.utcnow().timestamp())}",
                'flight_id': flight_id,
                'status': 'confirmed',
                'confirmation_code': f"CONF{random.randint(100000, 999999)}",
                'passenger_details': passenger_details,
                'booking_date': datetime.utcnow().isoformat(),
                'total_price': 299.99,
                'currency': 'USD'
            }
            
            return booking_confirmation
            
        except Exception as e:
            logging.error(f"Error booking flight: {str(e)}")
            return {'error': 'Booking failed'}
    
    def cancel_flight(self, booking_id: str) -> Dict[str, Any]:
        """Cancel a flight booking"""
        
        try:
            # In a real implementation, this would handle cancellation fees and refunds
            
            return {
                'booking_id': booking_id,
                'status': 'cancelled',
                'cancelled_at': datetime.utcnow().isoformat(),
                'refund_amount': 250.00,  # Example refund after fees
                'refund_status': 'processing'
            }
            
        except Exception as e:
            logging.error(f"Error cancelling flight: {str(e)}")
            return {'error': 'Cancellation failed'}
    
    def search_airports(self, query: str) -> List[Dict[str, Any]]:
        """Search for airports by name or code"""
        
        try:
            if not self._get_amadeus_token():
                return self._get_mock_airports(query)
            
            url = f"{self.amadeus_base_url}/reference-data/locations"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            params = {
                'keyword': query,
                'subType': 'AIRPORT',
                'page[limit]': 10
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_airports_response(data)
            else:
                return self._get_mock_airports(query)
                
        except Exception as e:
            logging.error(f"Error searching airports: {str(e)}")
            return self._get_mock_airports(query)
    
    def _get_mock_airports(self, query: str) -> List[Dict[str, Any]]:
        """Return mock airport data"""
        
        airports = [
            {'code': 'JFK', 'name': 'John F. Kennedy International Airport', 'city': 'New York', 'country': 'US'},
            {'code': 'LAX', 'name': 'Los Angeles International Airport', 'city': 'Los Angeles', 'country': 'US'},
            {'code': 'LHR', 'name': 'London Heathrow Airport', 'city': 'London', 'country': 'GB'},
            {'code': 'CDG', 'name': 'Charles de Gaulle Airport', 'city': 'Paris', 'country': 'FR'},
            {'code': 'NRT', 'name': 'Narita International Airport', 'city': 'Tokyo', 'country': 'JP'}
        ]
        
        # Filter based on query
        query_lower = query.lower()
        filtered = [
            airport for airport in airports
            if query_lower in airport['code'].lower() or 
               query_lower in airport['name'].lower() or 
               query_lower in airport['city'].lower()
        ]
        
        return filtered[:10]