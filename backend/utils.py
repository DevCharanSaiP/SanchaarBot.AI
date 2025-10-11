import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import hashlib
import uuid

def validate_email(email: str) -> bool:
    """Validate email address format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format (basic validation)"""
    # Remove all non-digit characters
    digits_only = re.sub(r'[^\d]', '', phone)
    # Check if it's between 10-15 digits
    return 10 <= len(digits_only) <= 15

def validate_date_format(date_string: str, format_string: str = '%Y-%m-%d') -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False

def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(input_string, str):
        return str(input_string)
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';]', '', input_string)
    
    # Limit length to prevent buffer overflow
    sanitized = sanitized[:1000]
    
    return sanitized.strip()

def generate_unique_id(prefix: str = '') -> str:
    """Generate a unique identifier"""
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id

def hash_string(input_string: str, algorithm: str = 'sha256') -> str:
    """Hash a string using specified algorithm"""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(input_string.encode('utf-8'))
    return hash_obj.hexdigest()

def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format currency amount for display"""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$'
    }
    
    symbol = currency_symbols.get(currency, currency + ' ')
    
    if currency == 'JPY':
        # Japanese Yen doesn't use decimal places
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"

def parse_date_range(date_string: str) -> Dict[str, Optional[datetime]]:
    """Parse various date range formats"""
    try:
        # Handle different date formats
        if ' - ' in date_string:
            start_str, end_str = date_string.split(' - ')
            start_date = parse_single_date(start_str.strip())
            end_date = parse_single_date(end_str.strip())
        elif ' to ' in date_string:
            start_str, end_str = date_string.split(' to ')
            start_date = parse_single_date(start_str.strip())
            end_date = parse_single_date(end_str.strip())
        else:
            # Single date
            start_date = parse_single_date(date_string.strip())
            end_date = start_date
        
        return {'start': start_date, 'end': end_date}
        
    except Exception as e:
        logging.error(f"Error parsing date range: {str(e)}")
        return {'start': None, 'end': None}

def parse_single_date(date_string: str) -> Optional[datetime]:
    """Parse a single date string in various formats"""
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None

def calculate_days_between(start_date: Union[str, datetime], end_date: Union[str, datetime]) -> int:
    """Calculate days between two dates"""
    try:
        if isinstance(start_date, str):
            start_date = parse_single_date(start_date)
        if isinstance(end_date, str):
            end_date = parse_single_date(end_date)
        
        if start_date and end_date:
            return (end_date - start_date).days
        
        return 0
        
    except Exception:
        return 0

def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable format"""
    if minutes < 60:
        return f"{minutes} minutes"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        return f"{hours} hour{'s' if hours != 1 else ''} {remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}"

def extract_location_components(location_string: str) -> Dict[str, str]:
    """Extract city, state, country from location string"""
    components = {'city': '', 'state': '', 'country': ''}
    
    try:
        parts = [part.strip() for part in location_string.split(',')]
        
        if len(parts) == 1:
            components['city'] = parts[0]
        elif len(parts) == 2:
            components['city'] = parts[0]
            components['country'] = parts[1]
        elif len(parts) >= 3:
            components['city'] = parts[0]
            components['state'] = parts[1]
            components['country'] = parts[-1]
        
        return components
        
    except Exception:
        return components

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula"""
    import math
    
    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to specified length with suffix"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)].strip()
    return truncated + suffix

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple implementation)"""
    # Remove punctuation and convert to lowercase
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Split into words
    words = clean_text.split()
    
    # Remove common stop words
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'this', 'but', 'they', 'have', 'had',
        'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their', 'if',
        'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
        'would', 'make', 'like', 'into', 'him', 'time', 'two', 'more', 'go',
        'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who',
        'did', 'get', 'may', 'day', 'use', 'water', 'part', 'oil', 'we', 'you'
    }
    
    # Filter out stop words and short words
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    
    # Count frequency and return most common
    word_count = {}
    for word in keywords:
        word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, count in sorted_keywords[:max_keywords]]

def validate_json(json_string: str) -> bool:
    """Validate JSON string"""
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False

def safe_json_parse(json_string: str, default: Any = None) -> Any:
    """Safely parse JSON string with default fallback"""
    try:
        return json.loads(json_string)
    except (ValueError, TypeError):
        return default

def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def mask_sensitive_info(text: str, mask_char: str = '*') -> str:
    """Mask sensitive information like email addresses, phone numbers"""
    # Mask email addresses
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 
                  lambda m: m.group()[:2] + mask_char * (len(m.group()) - 4) + m.group()[-2:], 
                  text)
    
    # Mask phone numbers (simple pattern)
    text = re.sub(r'\b\d{10,}\b', 
                  lambda m: m.group()[:3] + mask_char * (len(m.group()) - 6) + m.group()[-3:], 
                  text)
    
    return text

def paginate_list(items: List[Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """Paginate a list of items"""
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages))
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    return {
        'items': items[start_index:end_index],
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
    }

def retry_operation(func, max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """Retry an operation with exponential backoff"""
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = delay * (backoff_factor ** attempt)
            logging.warning(f"Operation failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {str(e)}")
            time.sleep(wait_time)

def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries with later ones taking precedence"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get value from nested dictionary using dot notation"""
    try:
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
        
    except Exception:
        return default

def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """Set value in nested dictionary using dot notation"""
    keys = path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return data

def deep_merge_dictionaries(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dictionaries(result[key], value)
        else:
            result[key] = value
    
    return result

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window  # seconds
        self.calls = []
    
    def is_allowed(self) -> bool:
        """Check if a call is allowed under rate limit"""
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        # Check if we can make a new call
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def time_until_next_call(self) -> float:
        """Get time in seconds until next call is allowed"""
        if not self.calls:
            return 0
        
        oldest_call = min(self.calls)
        return max(0, self.time_window - (time.time() - oldest_call))

def format_error_message(error: Exception, include_traceback: bool = False) -> Dict[str, Any]:
    """Format error message for consistent error responses"""
    import traceback
    
    error_info = {
        'error_type': type(error).__name__,
        'message': str(error),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if include_traceback:
        error_info['traceback'] = traceback.format_exc()
    
    return error_info