import requests
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
import random

class NewsAPI:
    """Client for news and travel advisory information"""
    
    def __init__(self):
        # NewsAPI.org credentials
        self.newsapi_key = os.environ.get('NEWSAPI_KEY')
        self.newsapi_base_url = 'https://newsapi.org/v2'
        
        # Alternative news sources
        self.guardian_api_key = os.environ.get('GUARDIAN_API_KEY')
        self.guardian_base_url = 'https://content.guardianapis.com'
        
        # Travel advisory APIs
        self.travel_advisories_base_url = 'https://www.travel-advisories.com/api'
        
    def get_travel_news(self, location: str, days_back: int = 7) -> Optional[Dict[str, Any]]:
        """Get travel-related news for a specific location"""
        
        try:
            if self.newsapi_key:
                return self._get_newsapi_travel_news(location, days_back)
            elif self.guardian_api_key:
                return self._get_guardian_travel_news(location, days_back)
            else:
                return self._get_mock_travel_news(location)
                
        except Exception as e:
            logging.error(f"Error getting travel news: {str(e)}")
            return self._get_mock_travel_news(location)
    
    def get_breaking_news(self, location: str = None) -> Optional[Dict[str, Any]]:
        """Get breaking news that might affect travel"""
        
        try:
            if self.newsapi_key:
                return self._get_newsapi_breaking_news(location)
            else:
                return self._get_mock_breaking_news(location)
                
        except Exception as e:
            logging.error(f"Error getting breaking news: {str(e)}")
            return self._get_mock_breaking_news(location)
    
    def _get_newsapi_travel_news(self, location: str, days_back: int) -> Optional[Dict[str, Any]]:
        """Get travel news from NewsAPI.org"""
        
        try:
            url = f"{self.newsapi_base_url}/everything"
            
            # Calculate date range
            from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            to_date = datetime.utcnow().strftime('%Y-%m-%d')
            
            # Create search query
            travel_keywords = [
                'travel', 'tourism', 'airport', 'airline', 'flight', 
                'hotel', 'border', 'visa', 'embassy', 'security alert'
            ]
            
            query = f'({location}) AND ({" OR ".join(travel_keywords)})'
            
            params = {
                'q': query,
                'from': from_date,
                'to': to_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 20,
                'apiKey': self.newsapi_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter and format articles
            articles = []
            for article in data.get('articles', []):
                if self._is_travel_relevant(article, location):
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'published_at': article.get('publishedAt', ''),
                        'author': article.get('author', ''),
                        'content_snippet': article.get('content', '')[:200] if article.get('content') else '',
                        'relevance_score': self._calculate_relevance(article, location),
                        'category': self._categorize_news(article)
                    })
            
            # Sort by relevance
            articles.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return {
                'location': location,
                'articles': articles[:10],  # Return top 10 most relevant
                'total_found': len(articles),
                'date_range': {
                    'from': from_date,
                    'to': to_date
                },
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'newsapi'
            }
            
        except Exception as e:
            logging.error(f"NewsAPI error: {str(e)}")
            return None
    
    def _get_guardian_travel_news(self, location: str, days_back: int) -> Optional[Dict[str, Any]]:
        """Get travel news from The Guardian API"""
        
        try:
            url = f"{self.guardian_base_url}/search"
            
            from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            params = {
                'q': f'{location} AND travel',
                'from-date': from_date,
                'show-fields': 'headline,byline,standfirst,body',
                'show-tags': 'keyword',
                'order-by': 'newest',
                'page-size': 20,
                'api-key': self.guardian_api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            articles = []
            for article in data.get('response', {}).get('results', []):
                articles.append({
                    'title': article.get('webTitle', ''),
                    'description': article.get('fields', {}).get('standfirst', ''),
                    'url': article.get('webUrl', ''),
                    'source': 'The Guardian',
                    'published_at': article.get('webPublicationDate', ''),
                    'author': article.get('fields', {}).get('byline', ''),
                    'content_snippet': article.get('fields', {}).get('body', '')[:200] if article.get('fields', {}).get('body') else '',
                    'relevance_score': 0.8,  # Guardian articles are generally high quality
                    'category': 'news'
                })
            
            return {
                'location': location,
                'articles': articles,
                'total_found': len(articles),
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'guardian'
            }
            
        except Exception as e:
            logging.error(f"Guardian API error: {str(e)}")
            return None
    
    def _get_newsapi_breaking_news(self, location: str = None) -> Optional[Dict[str, Any]]:
        """Get breaking news from NewsAPI.org"""
        
        try:
            url = f"{self.newsapi_base_url}/top-headlines"
            
            params = {
                'category': 'general',
                'language': 'en',
                'pageSize': 10,
                'apiKey': self.newsapi_key
            }
            
            if location:
                # Try to map location to country code
                country_code = self._location_to_country_code(location)
                if country_code:
                    params['country'] = country_code
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'author': article.get('author', ''),
                    'category': 'breaking_news',
                    'urgency': self._assess_urgency(article)
                })
            
            return {
                'location': location,
                'articles': articles,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'newsapi'
            }
            
        except Exception as e:
            logging.error(f"NewsAPI breaking news error: {str(e)}")
            return None
    
    def get_travel_advisories(self, country: str) -> Optional[Dict[str, Any]]:
        """Get official travel advisories for a country"""
        
        try:
            # This would integrate with official government APIs
            # For now, return mock data
            return self._get_mock_travel_advisories(country)
            
        except Exception as e:
            logging.error(f"Error getting travel advisories: {str(e)}")
            return self._get_mock_travel_advisories(country)
    
    def _get_mock_travel_news(self, location: str) -> Dict[str, Any]:
        """Return mock travel news data"""
        
        mock_articles = [
            {
                'title': f'New Flight Routes to {location} Announced',
                'description': f'Major airline announces new direct flights to {location}, improving connectivity for travelers.',
                'url': 'https://example.com/news1',
                'source': 'Travel Weekly',
                'published_at': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'author': 'Jane Smith',
                'content_snippet': f'The new routes to {location} will begin operating next month...',
                'relevance_score': 0.9,
                'category': 'transportation'
            },
            {
                'title': f'Tourism in {location} Shows Strong Recovery',
                'description': f'Latest statistics show tourism numbers in {location} are bouncing back.',
                'url': 'https://example.com/news2',
                'source': 'Tourism Today',
                'published_at': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                'author': 'Mike Johnson',
                'content_snippet': f'Visitor arrivals to {location} have increased by 25% compared to...',
                'relevance_score': 0.7,
                'category': 'tourism'
            },
            {
                'title': f'Weather Alert: Heavy Rain Expected in {location}',
                'description': f'Meteorologists warn of heavy rainfall in {location} region this week.',
                'url': 'https://example.com/news3',
                'source': 'Weather Central',
                'published_at': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                'author': 'Sarah Weather',
                'content_snippet': f'Heavy rain is expected to affect {location} starting tomorrow...',
                'relevance_score': 0.8,
                'category': 'weather'
            }
        ]
        
        return {
            'location': location,
            'articles': mock_articles,
            'total_found': len(mock_articles),
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'mock'
        }
    
    def _get_mock_breaking_news(self, location: str = None) -> Dict[str, Any]:
        """Return mock breaking news data"""
        
        mock_articles = [
            {
                'title': 'Airport Security Delays Expected',
                'description': 'Major airports experiencing longer security wait times due to increased screening procedures.',
                'url': 'https://example.com/breaking1',
                'source': 'Travel Alert Network',
                'published_at': (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                'author': 'Alert System',
                'category': 'breaking_news',
                'urgency': 'medium'
            },
            {
                'title': 'Currency Exchange Rate Fluctuations',
                'description': 'Significant changes in exchange rates affecting international travelers.',
                'url': 'https://example.com/breaking2',
                'source': 'Financial News',
                'published_at': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                'author': 'Finance Team',
                'category': 'breaking_news',
                'urgency': 'low'
            }
        ]
        
        return {
            'location': location,
            'articles': mock_articles,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'mock'
        }
    
    def _get_mock_travel_advisories(self, country: str) -> Dict[str, Any]:
        """Return mock travel advisory data"""
        
        advisory_levels = ['Exercise normal precautions', 'Exercise increased caution', 'Reconsider travel', 'Do not travel']
        
        return {
            'country': country,
            'advisory_level': random.choice(advisory_levels),
            'last_updated': datetime.utcnow().isoformat(),
            'summary': f'Current travel advisory for {country}. Check latest updates before traveling.',
            'details': [
                'Monitor local news and weather conditions',
                'Keep emergency contacts readily available',
                'Register with embassy if staying long-term'
            ],
            'health_notices': [
                'Ensure routine vaccinations are up to date',
                'Consider travel insurance coverage'
            ],
            'entry_requirements': {
                'passport_required': True,
                'visa_required': random.choice([True, False]),
                'covid_restrictions': 'Check current COVID-19 entry requirements'
            },
            'source': 'mock_advisory'
        }
    
    def _is_travel_relevant(self, article: Dict[str, Any], location: str) -> bool:
        """Check if an article is relevant to travel in the specified location"""
        
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        location_lower = location.lower()
        
        # Check for location mentions
        location_mentioned = location_lower in title or location_lower in description
        
        # Check for travel-related keywords
        travel_keywords = [
            'travel', 'tourism', 'airport', 'flight', 'hotel', 'border',
            'visa', 'embassy', 'security', 'alert', 'warning', 'advisory'
        ]
        
        travel_related = any(keyword in title or keyword in description for keyword in travel_keywords)
        
        return location_mentioned and travel_related
    
    def _calculate_relevance(self, article: Dict[str, Any], location: str) -> float:
        """Calculate relevance score for an article"""
        
        score = 0.0
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        location_lower = location.lower()
        
        # Location in title
        if location_lower in title:
            score += 0.5
        
        # Location in description
        if location_lower in description:
            score += 0.3
        
        # High-priority keywords
        priority_keywords = ['security alert', 'travel warning', 'embassy', 'border closure']
        for keyword in priority_keywords:
            if keyword in title or keyword in description:
                score += 0.4
                break
        
        # Medium-priority keywords
        medium_keywords = ['flight', 'airport', 'hotel', 'tourism']
        for keyword in medium_keywords:
            if keyword in title or keyword in description:
                score += 0.2
                break
        
        # Recency bonus
        published_at = article.get('publishedAt', '')
        try:
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            hours_old = (datetime.utcnow() - pub_date.replace(tzinfo=None)).total_seconds() / 3600
            
            if hours_old < 6:
                score += 0.2
            elif hours_old < 24:
                score += 0.1
        except:
            pass
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _categorize_news(self, article: Dict[str, Any]) -> str:
        """Categorize news article"""
        
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        if any(word in title or word in description for word in ['security', 'alert', 'warning', 'embassy']):
            return 'security'
        elif any(word in title or word in description for word in ['flight', 'airline', 'airport']):
            return 'transportation'
        elif any(word in title or word in description for word in ['weather', 'storm', 'hurricane', 'flood']):
            return 'weather'
        elif any(word in title or word in description for word in ['hotel', 'accommodation', 'booking']):
            return 'accommodation'
        elif any(word in title or word in description for word in ['tourism', 'attraction', 'festival']):
            return 'tourism'
        else:
            return 'general'
    
    def _assess_urgency(self, article: Dict[str, Any]) -> str:
        """Assess urgency level of news article"""
        
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        if any(word in title or word in description for word in ['breaking', 'urgent', 'emergency', 'immediate']):
            return 'high'
        elif any(word in title or word in description for word in ['alert', 'warning', 'advisory']):
            return 'medium'
        else:
            return 'low'
    
    def _location_to_country_code(self, location: str) -> Optional[str]:
        """Convert location name to ISO country code"""
        
        # Simplified mapping - in production, use a proper geocoding service
        country_mapping = {
            'united states': 'us',
            'usa': 'us',
            'united kingdom': 'gb',
            'uk': 'gb',
            'canada': 'ca',
            'australia': 'au',
            'germany': 'de',
            'france': 'fr',
            'japan': 'jp',
            'china': 'cn',
            'india': 'in',
            'brazil': 'br',
            'italy': 'it',
            'spain': 'es'
        }
        
        location_lower = location.lower()
        return country_mapping.get(location_lower)