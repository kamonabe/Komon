"""
HTTP connectivity check module.

Provides lightweight HTTP-based network connectivity checks.
"""

import logging
import requests

logger = logging.getLogger(__name__)


def check_http(url, timeout=10, method='GET'):
    """
    Check network connectivity using HTTP request.
    
    Args:
        url (str): Target URL
        timeout (int): Timeout in seconds (default: 10)
        method (str): HTTP method (GET, HEAD, POST) (default: GET)
    
    Returns:
        bool: True if HTTP request succeeds (2xx-3xx), False otherwise
    
    Examples:
        >>> check_http("https://www.google.com")
        True
        >>> check_http("https://api.example.com/health", method="HEAD")
        True
    """
    try:
        logger.debug("Checking HTTP: url=%s, method=%s, timeout=%d", url, method, timeout)
        
        # Execute HTTP request
        response = requests.request(
            method,
            url,
            timeout=timeout,
            allow_redirects=True
        )
        
        # Consider 2xx-3xx as success
        success = 200 <= response.status_code < 400
        
        if success:
            logger.debug("HTTP check succeeded: url=%s, status=%d", url, response.status_code)
        else:
            logger.warning("HTTP check failed: url=%s, status=%d", url, response.status_code)
        
        return success
        
    except requests.exceptions.Timeout:
        logger.warning("HTTP timeout: url=%s, timeout=%d", url, timeout)
        return False
        
    except requests.exceptions.ConnectionError as e:
        logger.warning("HTTP connection error: url=%s, error=%s", url, e)
        return False
        
    except requests.exceptions.RequestException as e:
        logger.error("HTTP check failed: url=%s, error=%s", url, e, exc_info=True)
        return False
        
    except Exception as e:
        logger.error("Unexpected error in HTTP check: url=%s, error=%s", url, e, exc_info=True)
        return False
