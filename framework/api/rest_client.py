"""
REST API client with retry logic and comprehensive logging
"""
import json
import requests
from typing import Dict, Any, Optional, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from framework.core.config_manager import config
from framework.core.logger import log
from framework.utils.redact import redact_payload, redact_dict, redact_headers
from requests.exceptions import RequestException, HTTPError


class RESTClient:
    """REST API client with retry logic and logging"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = base_url or config.api.api_base_url
        self.timeout = timeout or config.api.api_timeout
        self.session = requests.Session()
        
        # Configure retry strategy - ONLY for idempotent methods (GET, HEAD)
        # POST, PUT, DELETE should NOT be retried to prevent data corruption
        retry_strategy = Retry(
            total=config.base.retry_count,
            connect=0,
            read=0,
            redirect=0,
            status=config.base.retry_count,
            backoff_factor=config.base.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _log_request(self, method: str, url: str, **kwargs):
        """Log API request"""
        log.info(f"API Request: {method} {url}")
        if 'json' in kwargs:
            log.debug(f"Request Body: {redact_payload(kwargs['json'])}")
        if 'params' in kwargs:
            log.debug(f"Request Params: {kwargs['params']}")
        if 'headers' in kwargs:
            log.debug(f"Request Headers: {redact_headers(kwargs['headers'])}")
        elif self.session.headers:
            log.debug(f"Request Headers: {redact_headers(dict(self.session.headers))}")
    
    def _log_response(self, response: requests.Response):
        """Log API response"""
        log.info(f"API Response: {response.status_code} {response.reason}")
        try:
            response_json = response.json()
            safe_body = redact_payload(response_json)
            if isinstance(safe_body, dict) and len(str(safe_body)) > 1000:
                log.debug(f"Response Body (truncated): {str(safe_body)[:500]}...")
            else:
                log.debug(f"Response Body: {safe_body}")
        except (ValueError, json.JSONDecodeError):
            log.debug(f"Response Body: {response.text[:500]}")
        
        # Log retry information if available and attach to Allure
        history = getattr(response, 'history', None)
        if isinstance(history, (list, tuple)) and history:
            retry_count = len(history)
            log.warning(f"Request was retried {retry_count} times before success")
            
            # Attach retry information to Allure report
            try:
                import allure
                allure.attach(
                    f"Request was retried {retry_count} times before success.\n"
                    f"Final status: {response.status_code}\n"
                    f"Retry history: {[r.status_code for r in response.history]}",
                    name="Retry Information",
                    attachment_type=allure.attachment_type.TEXT
                )
            except ImportError:
                pass  # Allure not available
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith('http'):
            return endpoint
        base = self.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base}/{endpoint}"
    
    def set_header(self, key: str, value: str):
        """Set default header"""
        self.session.headers[key] = value
    
    def set_headers(self, headers: Dict[str, str]):
        """Set multiple default headers"""
        self.session.headers.update(headers)
    
    def set_auth(self, auth_type: str, credentials: Union[str, tuple]):
        """Set authentication"""
        if auth_type.lower() == "bearer":
            self.set_header("Authorization", f"Bearer {credentials}")
        elif auth_type.lower() == "basic":
            self.session.auth = credentials
        else:
            raise ValueError(f"Unsupported auth type: {auth_type}")
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """GET request - idempotent, safe to retry (retry handled by urllib3 adapter)"""
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        self._log_request("GET", url, params=params, headers=request_headers)
        
        # Retry logic handled by urllib3 adapter (configured in __init__)
        # Only retries on transient server errors (429, 500, 502, 503, 504)
        response = self.session.get(
            url,
            params=params,
            headers=request_headers,
            timeout=self.timeout,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """POST request - NOT retried to prevent duplicate creation
        
        Args:
            idempotency_key: Optional key for idempotent POST requests
        """
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        # Add idempotency key if provided
        if idempotency_key:
            request_headers["Idempotency-Key"] = idempotency_key
        
        self._log_request("POST", url, json=json, data=data, headers=request_headers)
        
        # POST is NOT retried - single attempt only to prevent duplicates
        response = self.session.post(
            url,
            json=json,
            data=data,
            headers=request_headers,
            timeout=self.timeout,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """PUT request - NOT retried to prevent state corruption"""
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        self._log_request("PUT", url, json=json, data=data, headers=request_headers)
        
        # PUT is NOT retried - single attempt only
        response = self.session.put(
            url,
            json=json,
            data=data,
            headers=request_headers,
            timeout=self.timeout,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """PATCH request - NOT retried to prevent state corruption"""
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        self._log_request("PATCH", url, json=json, data=data, headers=request_headers)
        
        # PATCH is NOT retried - single attempt only
        response = self.session.patch(
            url,
            json=json,
            data=data,
            headers=request_headers,
            timeout=self.timeout,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """DELETE request - NOT retried to prevent unintended deletions"""
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        self._log_request("DELETE", url, headers=request_headers)
        
        # DELETE is NOT retried - single attempt only
        response = self.session.delete(
            url,
            headers=request_headers,
            timeout=self.timeout,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def close(self):
        """Close session"""
        self.session.close()
