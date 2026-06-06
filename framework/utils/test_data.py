"""
Test data management with YAML/JSON support and Faker integration
"""
import json
import yaml
import uuid
import time
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from faker import Faker
from framework.core.config_manager import config
from framework.core.logger import log


class TestDataManager:
    """Manages test data from files and generates dynamic data"""
    
    def __init__(self):
        self.faker = Faker()
        self.data_dir = Path(config.base.test_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Any] = {}
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load data from YAML file"""
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Test data file not found: {file_path}")
        
        if str(file_path) in self._cache:
            return self._cache[str(file_path)]
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f) or {}
            self._cache[str(file_path)] = data
            log.debug(f"Loaded test data from {file_path}")
            return data
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file"""
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Test data file not found: {file_path}")
        
        if str(file_path) in self._cache:
            return self._cache[str(file_path)]
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            self._cache[str(file_path)] = data
            log.debug(f"Loaded test data from {file_path}")
            return data
    
    def get(self, filename: str, key: str, default: Any = None) -> Any:
        """Get value from test data file by key (supports dot notation)"""
        try:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                data = self.load_yaml(filename)
            elif filename.endswith('.json'):
                data = self.load_json(filename)
            else:
                try:
                    data = self.load_yaml(filename)
                except FileNotFoundError:
                    data = self.load_json(filename)
        except FileNotFoundError:
            return default
        
        # Navigate nested keys
        keys = key.split('.')
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def _generate_unique_id(self) -> str:
        """Generate unique ID for test data isolation"""
        # Combine UUID, timestamp, and worker ID for parallel execution safety
        unique_id = str(uuid.uuid4())[:8]
        timestamp = int(time.time() * 1000)  # milliseconds
        worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
        return f"{unique_id}_{timestamp}_{worker_id}"
    
    def generate_user_data(self, **overrides) -> Dict[str, Any]:
        """Generate fake user data with guaranteed uniqueness for parallel execution"""
        unique_id = self._generate_unique_id()
        base_email = self.faker.email()
        # Extract domain from faker email or use default
        email_parts = base_email.split('@')
        domain = email_parts[1] if len(email_parts) > 1 else "example.com"
        
        data = {
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "email": f"test_{unique_id}@{domain}",  # Guaranteed unique
            "username": f"user_{unique_id}",  # Guaranteed unique
            "phone": self.faker.phone_number(),
            "address": self.faker.address(),
            "city": self.faker.city(),
            "country": self.faker.country(),
            "zipcode": self.faker.zipcode(),
            "date_of_birth": self.faker.date_of_birth().isoformat(),
            "password": "SecureTestPass123!",
        }
        data.update(overrides)
        return data
    
    def generate_product_data(self, **overrides) -> Dict[str, Any]:
        """Generate fake product data with guaranteed unique SKU"""
        unique_id = self._generate_unique_id()
        data = {
            "name": f"{self.faker.word().title()}_{unique_id[:8]}",
            "description": self.faker.text(),
            "price": round(self.faker.pyfloat(left_digits=3, right_digits=2, positive=True), 2),
            "sku": f"SKU-{unique_id}",  # Guaranteed unique
            "category": self.faker.word(),
            "stock": self.faker.random_int(min=0, max=1000),
        }
        data.update(overrides)
        return data
    
    def generate_order_data(self, **overrides) -> Dict[str, Any]:
        """Generate fake order data with guaranteed unique order number"""
        unique_id = self._generate_unique_id()
        data = {
            "order_number": f"ORD-{unique_id}",  # Guaranteed unique
            "total_amount": round(self.faker.pyfloat(left_digits=3, right_digits=2, positive=True), 2),
            "currency": "USD",
            "status": self.faker.random_element(elements=("pending", "processing", "shipped", "delivered")),
        }
        data.update(overrides)
        return data
    
    def generate_email(self, domain: Optional[str] = None) -> str:
        """Generate fake email with guaranteed uniqueness"""
        unique_id = self._generate_unique_id()
        if domain:
            return f"test_{unique_id}@{domain}"
        base_email = self.faker.email()
        email_parts = base_email.split('@')
        domain = email_parts[1] if len(email_parts) > 1 else "example.com"
        return f"test_{unique_id}@{domain}"
    
    def generate_string(self, length: int = 10, prefix: str = "") -> str:
        """Generate random string; without prefix, length is total size; with prefix, length is suffix size."""
        target_length = len(prefix) + length if prefix else length
        if len(prefix) >= target_length:
            return prefix[:target_length]
        remaining = target_length - len(prefix)
        unique_part = self._generate_unique_id()[: min(8, remaining)]
        remaining -= len(unique_part)
        random_part = self.faker.lexify(text='?' * remaining) if remaining > 0 else ""
        return f"{prefix}{unique_part}{random_part}"
    
    def generate_number(self, min_value: int = 0, max_value: int = 1000) -> int:
        """Generate random number"""
        return self.faker.random_int(min=min_value, max=max_value)
    
    def generate_date(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """Generate random date"""
        if start_date and end_date:
            result = self.faker.date_between(start_date=start_date, end_date=end_date)
        else:
            result = self.faker.date()
        if hasattr(result, "isoformat"):
            return result.isoformat()
        return str(result)
    
    def clear_cache(self):
        """Clear cached test data"""
        self._cache.clear()
        log.debug("Test data cache cleared")


# Global instance
test_data = TestDataManager()
