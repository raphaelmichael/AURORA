"""
Aurora Sentinel - API Manager
Handles external API connections with timeout and rate limiting
"""

import requests
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from threading import Lock


@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    name: str
    url: str
    timeout: int = 5
    rate_limit: float = 1.0  # requests per second
    headers: Optional[Dict[str, str]] = None


class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self, max_requests_per_second: float = 1.0):
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0
        self.lock = Lock()
        
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
                
            self.last_request_time = time.time()


class APIManager:
    """Manages external API connections with safety features"""
    
    def __init__(self):
        self.logger = logging.getLogger("Aurora_APIManager")
        self.endpoints = {}
        self.rate_limiters = {}
        self.stats = {}
        
        # Default public APIs
        self._setup_default_apis()
        
    def _setup_default_apis(self):
        """Setup default safe public APIs"""
        default_apis = [
            APIEndpoint(
                name="quotes",
                url="https://api.quotable.io/random",
                timeout=5,
                rate_limit=0.5
            ),
            APIEndpoint(
                name="jokes",
                url="https://official-joke-api.appspot.com/random_joke",
                timeout=5,
                rate_limit=0.5
            ),
            APIEndpoint(
                name="advice",
                url="https://api.adviceslip.com/advice",
                timeout=5,
                rate_limit=0.3
            )
        ]
        
        for api in default_apis:
            self.register_api(api)
            
    def register_api(self, endpoint: APIEndpoint):
        """Register a new API endpoint"""
        self.endpoints[endpoint.name] = endpoint
        self.rate_limiters[endpoint.name] = RateLimiter(endpoint.rate_limit)
        self.stats[endpoint.name] = {
            'success_count': 0,
            'error_count': 0,
            'last_success': None,
            'last_error': None
        }
        self.logger.info(f"Registered API: {endpoint.name}")
        
    def call_api(self, api_name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make a safe API call with rate limiting and error handling"""
        if api_name not in self.endpoints:
            self.logger.error(f"Unknown API: {api_name}")
            return None
            
        endpoint = self.endpoints[api_name]
        rate_limiter = self.rate_limiters[api_name]
        
        # Apply rate limiting
        rate_limiter.wait_if_needed()
        
        try:
            # Prepare request parameters
            headers = endpoint.headers or {}
            headers.update(kwargs.get('headers', {}))
            
            params = kwargs.get('params', {})
            timeout = kwargs.get('timeout', endpoint.timeout)
            
            self.logger.debug(f"Calling API: {api_name} -> {endpoint.url}")
            
            # Make the request
            response = requests.get(
                endpoint.url,
                headers=headers,
                params=params,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            # Parse response
            try:
                data = response.json()
            except ValueError:
                data = {'content': response.text}
                
            # Update stats
            self.stats[api_name]['success_count'] += 1
            self.stats[api_name]['last_success'] = time.time()
            
            self.logger.info(f"API call successful: {api_name}")
            return {
                'api_name': api_name,
                'status': 'success',
                'data': data,
                'timestamp': time.time()
            }
            
        except requests.exceptions.Timeout:
            error_msg = f"API timeout: {api_name}"
            self.logger.warning(error_msg)
            self._record_error(api_name, error_msg)
            return None
            
        except requests.exceptions.ConnectionError:
            error_msg = f"API connection error: {api_name}"
            self.logger.warning(error_msg)
            self._record_error(api_name, error_msg)
            return None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"API HTTP error {e.response.status_code}: {api_name}"
            self.logger.warning(error_msg)
            self._record_error(api_name, error_msg)
            return None
            
        except Exception as e:
            error_msg = f"API unexpected error: {api_name} - {str(e)}"
            self.logger.error(error_msg)
            self._record_error(api_name, error_msg)
            return None
            
    def _record_error(self, api_name: str, error_msg: str):
        """Record API error in stats"""
        self.stats[api_name]['error_count'] += 1
        self.stats[api_name]['last_error'] = {
            'timestamp': time.time(),
            'message': error_msg
        }
        
    def get_random_api_call(self) -> Optional[Dict[str, Any]]:
        """Make a call to a random available API"""
        import random
        
        available_apis = list(self.endpoints.keys())
        if not available_apis:
            self.logger.warning("No APIs available")
            return None
            
        api_name = random.choice(available_apis)
        return self.call_api(api_name)
        
    def get_api_stats(self, api_name: str = None) -> Dict[str, Any]:
        """Get statistics for specific API or all APIs"""
        if api_name:
            if api_name in self.stats:
                return {api_name: self.stats[api_name]}
            else:
                return {}
        else:
            return self.stats.copy()
            
    def get_healthy_apis(self) -> List[str]:
        """Get list of APIs that are currently healthy"""
        healthy_apis = []
        current_time = time.time()
        
        for api_name, stats in self.stats.items():
            # Consider healthy if recent success or no recent errors
            recent_success = stats.get('last_success', 0) > current_time - 300  # 5 minutes
            recent_error = stats.get('last_error', {}).get('timestamp', 0) > current_time - 300
            
            if recent_success or not recent_error:
                healthy_apis.append(api_name)
                
        return healthy_apis
        
    def test_all_apis(self) -> Dict[str, bool]:
        """Test all registered APIs"""
        results = {}
        
        for api_name in self.endpoints.keys():
            result = self.call_api(api_name)
            results[api_name] = result is not None
            
        self.logger.info(f"API test results: {results}")
        return results
        
    def cleanup_stats(self, max_age_hours: int = 24):
        """Clean up old statistics"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for api_name, stats in self.stats.items():
            # Reset old error records
            if stats.get('last_error'):
                error_age = current_time - stats['last_error'].get('timestamp', 0)
                if error_age > max_age_seconds:
                    stats['last_error'] = None
                    
        self.logger.info("API stats cleanup completed")