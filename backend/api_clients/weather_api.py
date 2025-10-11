import requests
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os

class WeatherAPI:
    """Client for weather data and forecasts"""
    
    def __init__(self):
        # OpenWeatherMap API credentials
        self.openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')
        self.openweather_base_url = 'https://api.openweathermap.org/data/2.5'
        
        # WeatherAPI.com credentials (alternative)
        self.weatherapi_key = os.environ.get('WEATHERAPI_KEY')
        self.weatherapi_base_url = 'https://api.weatherapi.com/v1'
        
    def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Get current weather for a location"""
        
        try:
            if self.openweather_api_key:
                return self._get_openweather_current(location)
            elif self.weatherapi_key:
                return self._get_weatherapi_current(location)
            else:
                return self._get_mock_current_weather(location)
                
        except Exception as e:
            logging.error(f"Error getting current weather: {str(e)}")
            return self._get_mock_current_weather(location)
    
    def get_forecast(self, location: str, days: int = 5) -> Optional[Dict[str, Any]]:
        """Get weather forecast for a location"""
        
        try:
            if self.openweather_api_key:
                return self._get_openweather_forecast(location, days)
            elif self.weatherapi_key:
                return self._get_weatherapi_forecast(location, days)
            else:
                return self._get_mock_forecast(location, days)
                
        except Exception as e:
            logging.error(f"Error getting weather forecast: {str(e)}")
            return self._get_mock_forecast(location, days)
    
    def _get_openweather_current(self, location: str) -> Optional[Dict[str, Any]]:
        """Get current weather from OpenWeatherMap"""
        
        try:
            url = f"{self.openweather_base_url}/weather"
            
            params = {
                'q': location,
                'appid': self.openweather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'location': {
                    'name': data.get('name', location),
                    'country': data.get('sys', {}).get('country', ''),
                    'coordinates': {
                        'latitude': data.get('coord', {}).get('lat', 0),
                        'longitude': data.get('coord', {}).get('lon', 0)
                    }
                },
                'current': {
                    'temperature': data.get('main', {}).get('temp', 0),
                    'feels_like': data.get('main', {}).get('feels_like', 0),
                    'humidity': data.get('main', {}).get('humidity', 0),
                    'pressure': data.get('main', {}).get('pressure', 0),
                    'description': data.get('weather', [{}])[0].get('description', ''),
                    'icon': data.get('weather', [{}])[0].get('icon', ''),
                    'wind_speed': data.get('wind', {}).get('speed', 0),
                    'wind_direction': data.get('wind', {}).get('deg', 0),
                    'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                    'uv_index': 0  # OpenWeatherMap doesn't include UV in current weather
                },
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'openweathermap'
            }
            
        except Exception as e:
            logging.error(f"OpenWeatherMap API error: {str(e)}")
            return None
    
    def _get_openweather_forecast(self, location: str, days: int) -> Optional[Dict[str, Any]]:
        """Get forecast from OpenWeatherMap"""
        
        try:
            url = f"{self.openweather_base_url}/forecast"
            
            params = {
                'q': location,
                'appid': self.openweather_api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Group forecasts by day
            daily_forecasts = []
            current_date = None
            current_day = None
            
            for forecast in data.get('list', []):
                forecast_date = datetime.fromtimestamp(forecast.get('dt', 0)).date()
                
                if forecast_date != current_date:
                    if current_day:
                        daily_forecasts.append(current_day)
                    
                    current_date = forecast_date
                    current_day = {
                        'date': forecast_date.isoformat(),
                        'temperature': {
                            'min': forecast.get('main', {}).get('temp_min', 0),
                            'max': forecast.get('main', {}).get('temp_max', 0),
                            'avg': forecast.get('main', {}).get('temp', 0)
                        },
                        'conditions': {
                            'description': forecast.get('weather', [{}])[0].get('description', ''),
                            'icon': forecast.get('weather', [{}])[0].get('icon', '')
                        },
                        'humidity': forecast.get('main', {}).get('humidity', 0),
                        'wind_speed': forecast.get('wind', {}).get('speed', 0),
                        'precipitation': forecast.get('rain', {}).get('3h', 0) + forecast.get('snow', {}).get('3h', 0)
                    }
                else:
                    # Update min/max temperatures
                    temp = forecast.get('main', {}).get('temp', 0)
                    current_day['temperature']['min'] = min(current_day['temperature']['min'], temp)
                    current_day['temperature']['max'] = max(current_day['temperature']['max'], temp)
            
            if current_day:
                daily_forecasts.append(current_day)
            
            return {
                'location': {
                    'name': data.get('city', {}).get('name', location),
                    'country': data.get('city', {}).get('country', ''),
                    'coordinates': {
                        'latitude': data.get('city', {}).get('coord', {}).get('lat', 0),
                        'longitude': data.get('city', {}).get('coord', {}).get('lon', 0)
                    }
                },
                'forecast': daily_forecasts[:days],
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'openweathermap'
            }
            
        except Exception as e:
            logging.error(f"OpenWeatherMap forecast API error: {str(e)}")
            return None
    
    def _get_weatherapi_current(self, location: str) -> Optional[Dict[str, Any]]:
        """Get current weather from WeatherAPI.com"""
        
        try:
            url = f"{self.weatherapi_base_url}/current.json"
            
            params = {
                'key': self.weatherapi_key,
                'q': location,
                'aqi': 'no'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            location_data = data.get('location', {})
            current_data = data.get('current', {})
            
            return {
                'location': {
                    'name': location_data.get('name', location),
                    'country': location_data.get('country', ''),
                    'coordinates': {
                        'latitude': location_data.get('lat', 0),
                        'longitude': location_data.get('lon', 0)
                    }
                },
                'current': {
                    'temperature': current_data.get('temp_c', 0),
                    'feels_like': current_data.get('feelslike_c', 0),
                    'humidity': current_data.get('humidity', 0),
                    'pressure': current_data.get('pressure_mb', 0),
                    'description': current_data.get('condition', {}).get('text', ''),
                    'icon': current_data.get('condition', {}).get('icon', ''),
                    'wind_speed': current_data.get('wind_kph', 0),
                    'wind_direction': current_data.get('wind_degree', 0),
                    'visibility': current_data.get('vis_km', 0),
                    'uv_index': current_data.get('uv', 0)
                },
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'weatherapi'
            }
            
        except Exception as e:
            logging.error(f"WeatherAPI.com error: {str(e)}")
            return None
    
    def _get_weatherapi_forecast(self, location: str, days: int) -> Optional[Dict[str, Any]]:
        """Get forecast from WeatherAPI.com"""
        
        try:
            url = f"{self.weatherapi_base_url}/forecast.json"
            
            params = {
                'key': self.weatherapi_key,
                'q': location,
                'days': min(days, 10),  # WeatherAPI.com supports up to 10 days
                'aqi': 'no',
                'alerts': 'yes'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            location_data = data.get('location', {})
            forecast_data = data.get('forecast', {}).get('forecastday', [])
            
            daily_forecasts = []
            
            for day in forecast_data:
                day_data = day.get('day', {})
                
                daily_forecast = {
                    'date': day.get('date', ''),
                    'temperature': {
                        'min': day_data.get('mintemp_c', 0),
                        'max': day_data.get('maxtemp_c', 0),
                        'avg': day_data.get('avgtemp_c', 0)
                    },
                    'conditions': {
                        'description': day_data.get('condition', {}).get('text', ''),
                        'icon': day_data.get('condition', {}).get('icon', '')
                    },
                    'humidity': day_data.get('avghumidity', 0),
                    'wind_speed': day_data.get('maxwind_kph', 0),
                    'precipitation': day_data.get('totalprecip_mm', 0),
                    'uv_index': day_data.get('uv', 0)
                }
                
                daily_forecasts.append(daily_forecast)
            
            return {
                'location': {
                    'name': location_data.get('name', location),
                    'country': location_data.get('country', ''),
                    'coordinates': {
                        'latitude': location_data.get('lat', 0),
                        'longitude': location_data.get('lon', 0)
                    }
                },
                'forecast': daily_forecasts,
                'alerts': data.get('alerts', {}).get('alert', []),
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'weatherapi'
            }
            
        except Exception as e:
            logging.error(f"WeatherAPI.com forecast error: {str(e)}")
            return None
    
    def _get_mock_current_weather(self, location: str) -> Dict[str, Any]:
        """Return mock current weather data"""
        
        import random
        
        conditions = [
            'Clear', 'Partly Cloudy', 'Cloudy', 'Light Rain', 
            'Heavy Rain', 'Sunny', 'Overcast', 'Fog'
        ]
        
        return {
            'location': {
                'name': location,
                'country': 'Unknown',
                'coordinates': {
                    'latitude': random.uniform(-90, 90),
                    'longitude': random.uniform(-180, 180)
                }
            },
            'current': {
                'temperature': random.randint(10, 35),
                'feels_like': random.randint(8, 38),
                'humidity': random.randint(30, 90),
                'pressure': random.randint(980, 1030),
                'description': random.choice(conditions),
                'icon': '01d',
                'wind_speed': random.randint(0, 25),
                'wind_direction': random.randint(0, 360),
                'visibility': random.randint(5, 15),
                'uv_index': random.randint(1, 10)
            },
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'mock'
        }
    
    def _get_mock_forecast(self, location: str, days: int) -> Dict[str, Any]:
        """Return mock forecast data"""
        
        import random
        
        conditions = [
            'Clear', 'Partly Cloudy', 'Cloudy', 'Light Rain', 
            'Heavy Rain', 'Sunny', 'Overcast', 'Thunderstorm'
        ]
        
        daily_forecasts = []
        
        for i in range(days):
            forecast_date = (datetime.utcnow() + timedelta(days=i)).date()
            
            daily_forecast = {
                'date': forecast_date.isoformat(),
                'temperature': {
                    'min': random.randint(5, 20),
                    'max': random.randint(20, 35),
                    'avg': random.randint(10, 28)
                },
                'conditions': {
                    'description': random.choice(conditions),
                    'icon': random.choice(['01d', '02d', '03d', '04d', '09d', '10d', '11d'])
                },
                'humidity': random.randint(40, 85),
                'wind_speed': random.randint(5, 20),
                'precipitation': random.uniform(0, 10),
                'uv_index': random.randint(1, 10)
            }
            
            daily_forecasts.append(daily_forecast)
        
        return {
            'location': {
                'name': location,
                'country': 'Unknown',
                'coordinates': {
                    'latitude': random.uniform(-90, 90),
                    'longitude': random.uniform(-180, 180)
                }
            },
            'forecast': daily_forecasts,
            'alerts': [],
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'mock'
        }
    
    def get_weather_alerts(self, location: str) -> List[Dict[str, Any]]:
        """Get weather alerts for a location"""
        
        try:
            if self.weatherapi_key:
                return self._get_weatherapi_alerts(location)
            else:
                return self._get_mock_alerts(location)
                
        except Exception as e:
            logging.error(f"Error getting weather alerts: {str(e)}")
            return []
    
    def _get_weatherapi_alerts(self, location: str) -> List[Dict[str, Any]]:
        """Get weather alerts from WeatherAPI.com"""
        
        try:
            url = f"{self.weatherapi_base_url}/current.json"
            
            params = {
                'key': self.weatherapi_key,
                'q': location,
                'alerts': 'yes'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            alerts_data = data.get('alerts', {}).get('alert', [])
            
            alerts = []
            for alert in alerts_data:
                alerts.append({
                    'title': alert.get('headline', ''),
                    'description': alert.get('desc', ''),
                    'severity': alert.get('severity', ''),
                    'areas': alert.get('areas', ''),
                    'category': alert.get('category', ''),
                    'effective': alert.get('effective', ''),
                    'expires': alert.get('expires', ''),
                    'instruction': alert.get('instruction', '')
                })
            
            return alerts
            
        except Exception as e:
            logging.error(f"Error getting WeatherAPI alerts: {str(e)}")
            return []
    
    def _get_mock_alerts(self, location: str) -> List[Dict[str, Any]]:
        """Return mock weather alerts"""
        
        import random
        
        if random.random() < 0.2:  # 20% chance of alerts
            return [
                {
                    'title': f'Weather Advisory for {location}',
                    'description': 'Moderate to heavy rain expected in the area. Exercise caution when traveling.',
                    'severity': 'Moderate',
                    'areas': location,
                    'category': 'Rain',
                    'effective': datetime.utcnow().isoformat(),
                    'expires': (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                    'instruction': 'Avoid unnecessary travel. Carry umbrella if going out.'
                }
            ]
        
        return []