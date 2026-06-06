"""
API response validators and schema validation
"""
import json
from typing import Dict, Any, Optional, List
import jsonschema
from jsonschema import ValidationError as JsonSchemaValidationError
from framework.core.logger import log
from framework.utils.assertions import hard_assert, AssertionError


class APIResponseValidator:
    """Validates API responses"""
    
    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        try:
            self.json_data = response.json()
        except (ValueError, json.JSONDecodeError):
            self.json_data = None
        self.text = response.text
    
    def assert_status_code(self, expected_code: int, message: Optional[str] = None):
        """Assert response status code"""
        msg = message or f"Expected status code {expected_code}, but got {self.status_code}"
        hard_assert.assert_equal(self.status_code, expected_code, msg)
        log.info(f"Status code assertion passed: {self.status_code}")
    
    def assert_status_code_in(self, expected_codes: List[int], message: Optional[str] = None):
        """Assert response status code is in list"""
        msg = message or f"Expected status code in {expected_codes}, but got {self.status_code}"
        hard_assert.assert_in(self.status_code, expected_codes, msg)
        log.info(f"Status code assertion passed: {self.status_code}")
    
    def assert_json_schema(self, schema: Dict[str, Any], message: Optional[str] = None):
        """Assert response matches a JSON Schema or legacy flat key/type map."""
        if self.json_data is None:
            raise AssertionError(
                message="Response is not JSON",
                context={"status_code": self.response.status_code if hasattr(self, 'response') else None}
            )

        if any(key in schema for key in ("type", "properties", "$schema", "required")):
            try:
                jsonschema.validate(instance=self.json_data, schema=schema)
            except JsonSchemaValidationError as error:
                raise AssertionError(
                    message=message or str(error.message),
                    actual=self.json_data,
                    expected=schema,
                    context={"json_path": list(error.absolute_path)},
                ) from error
            log.info("JSON schema validation passed")
            return

        for key, expected_type in schema.items():
            if key not in self.json_data:
                raise AssertionError(
                    message=f"Key '{key}' not found in response",
                    expected=key,
                    actual=list(self.json_data.keys()) if self.json_data else None,
                    context={"schema_keys": list(schema.keys())}
                )
            
            actual_type = type(self.json_data[key]).__name__
            expected_type_name = expected_type.__name__ if hasattr(expected_type, '__name__') else str(expected_type)
            
            if not isinstance(self.json_data[key], expected_type):
                msg = message or f"Key '{key}' type mismatch: expected {expected_type_name}, got {actual_type}"
                raise AssertionError(
                    message=msg,
                    expected=expected_type_name,
                    actual=actual_type,
                    context={"key": key, "value": self.json_data[key]}
                )
        
        log.info("JSON schema validation passed")
    
    def assert_contains_key(self, key: str, message: Optional[str] = None):
        """Assert response contains key"""
        if self.json_data is None:
            raise AssertionError(
                message="Response is not JSON",
                context={"status_code": self.response.status_code}
            )
        
        msg = message or f"Key '{key}' not found in response"
        hard_assert.assert_in(key, self.json_data, msg)
        log.info(f"Key '{key}' found in response")
    
    def assert_key_value(self, key: str, expected_value: Any, message: Optional[str] = None):
        """Assert key has expected value"""
        if self.json_data is None:
            raise AssertionError(
                message="Response is not JSON",
                context={"status_code": self.response.status_code}
            )
        
        self.assert_contains_key(key)
        actual_value = self.json_data[key]
        msg = message or f"Key '{key}' value mismatch: expected {expected_value}, got {actual_value}"
        hard_assert.assert_equal(actual_value, expected_value, msg)
        log.info(f"Key '{key}' value assertion passed")
    
    def assert_response_time(self, max_time_ms: int, message: Optional[str] = None):
        """Assert response time is within limit"""
        response_time_ms = self.response.elapsed.total_seconds() * 1000
        msg = message or f"Response time {response_time_ms}ms exceeds limit {max_time_ms}ms"
        hard_assert.assert_less_than(response_time_ms, max_time_ms, msg)
        log.info(f"Response time assertion passed: {response_time_ms}ms")
    
    def assert_header(self, header_name: str, expected_value: Optional[str] = None, message: Optional[str] = None):
        """Assert response header exists and optionally matches value"""
        if header_name not in self.response.headers:
            msg = message or f"Header '{header_name}' not found in response"
            raise AssertionError(
                message=msg,
                expected=header_name,
                actual=list(self.response.headers.keys()),
                context={"available_headers": list(self.response.headers.keys())}
            )
        
        if expected_value is not None:
            actual_value = self.response.headers[header_name]
            msg = message or f"Header '{header_name}' value mismatch: expected {expected_value}, got {actual_value}"
            hard_assert.assert_equal(actual_value, expected_value, msg)
        
        log.info(f"Header '{header_name}' assertion passed")
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get value from JSON response by key (supports dot notation)"""
        if self.json_data is None:
            return default
        
        keys = key.split('.')
        value = self.json_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        
        return value
