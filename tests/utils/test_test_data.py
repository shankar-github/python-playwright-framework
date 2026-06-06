"""
Tests for test data manager
"""
import pytest
import tempfile
import json
import yaml
from pathlib import Path
from framework.utils.test_data import TestDataManager


class TestTestDataManager:
    """Tests for TestDataManager"""
    
    def test_load_yaml(self):
        """Test loading YAML file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test YAML file
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text("""
test_data:
  user:
    name: "Test User"
    email: "test@example.com"
""")
            
            manager = TestDataManager()
            manager.data_dir = Path(tmpdir)
            
            data = manager.load_yaml("test.yaml")
            
            assert "test_data" in data, "Should load YAML data"
            assert data["test_data"]["user"]["name"] == "Test User", "Should parse YAML correctly"
    
    def test_load_json(self):
        """Test loading JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test JSON file
            json_file = Path(tmpdir) / "test.json"
            json_file.write_text(json.dumps({
                "test_data": {
                    "user": {
                        "name": "Test User",
                        "email": "test@example.com"
                    }
                }
            }))
            
            manager = TestDataManager()
            manager.data_dir = Path(tmpdir)
            
            data = manager.load_json("test.json")
            
            assert "test_data" in data, "Should load JSON data"
            assert data["test_data"]["user"]["name"] == "Test User", "Should parse JSON correctly"
    
    def test_get_method(self):
        """Test get method with dot notation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text("""
user:
  name: "Test User"
  email: "test@example.com"
""")
            
            manager = TestDataManager()
            manager.data_dir = Path(tmpdir)
            
            name = manager.get("test.yaml", "user.name")
            email = manager.get("test.yaml", "user.email")
            
            assert name == "Test User", "Should get nested value"
            assert email == "test@example.com", "Should get nested value"
    
    def test_get_with_default(self):
        """Test get method with default value"""
        manager = TestDataManager()
        
        value = manager.get("non_existent.yaml", "key", "default")
        assert value == "default", "Should return default value"
    
    def test_generate_user_data(self):
        """Test generating user data"""
        manager = TestDataManager()
        
        user_data = manager.generate_user_data()
        
        assert "first_name" in user_data, "Should have first_name"
        assert "last_name" in user_data, "Should have last_name"
        assert "email" in user_data, "Should have email"
        assert "@" in user_data["email"], "Email should be valid format"
    
    def test_generate_user_data_with_overrides(self):
        """Test generating user data with overrides"""
        manager = TestDataManager()
        
        user_data = manager.generate_user_data(email="custom@example.com")
        
        assert user_data["email"] == "custom@example.com", "Should use override value"
        assert "first_name" in user_data, "Should still have other fields"
    
    def test_generate_product_data(self):
        """Test generating product data"""
        manager = TestDataManager()
        
        product_data = manager.generate_product_data()
        
        assert "name" in product_data, "Should have name"
        assert "price" in product_data, "Should have price"
        assert "sku" in product_data, "Should have sku"
        assert isinstance(product_data["price"], float), "Price should be float"
    
    def test_generate_order_data(self):
        """Test generating order data"""
        manager = TestDataManager()
        
        order_data = manager.generate_order_data()
        
        assert "order_number" in order_data, "Should have order_number"
        assert "total_amount" in order_data, "Should have total_amount"
        assert "status" in order_data, "Should have status"
    
    def test_generate_email(self):
        """Test generating email"""
        manager = TestDataManager()
        
        email = manager.generate_email()
        
        assert "@" in email, "Should be valid email format"
        assert "." in email.split("@")[1], "Should have domain"
    
    def test_generate_email_with_domain(self):
        """Test generating email with custom domain"""
        manager = TestDataManager()
        
        email = manager.generate_email(domain="example.com")
        
        assert email.endswith("@example.com"), "Should use custom domain"
    
    def test_generate_string(self):
        """Test generating random string"""
        manager = TestDataManager()
        
        string = manager.generate_string(length=10)
        
        assert len(string) == 10, "Should have correct length"
        assert isinstance(string, str), "Should be string"
    
    def test_generate_string_with_prefix(self):
        """Test generating string with prefix"""
        manager = TestDataManager()
        
        string = manager.generate_string(length=5, prefix="TEST_")
        
        assert string.startswith("TEST_"), "Should have prefix"
        assert len(string) == 10, "Should include prefix in length"
    
    def test_generate_number(self):
        """Test generating random number"""
        manager = TestDataManager()
        
        number = manager.generate_number(min_value=1, max_value=10)
        
        assert 1 <= number <= 10, "Should be in range"
        assert isinstance(number, int), "Should be integer"
    
    def test_generate_date(self):
        """Test generating date"""
        manager = TestDataManager()
        
        date = manager.generate_date()
        
        assert isinstance(date, str), "Should be string"
        assert len(date) == 10, "Should be ISO date format (YYYY-MM-DD)"
    
    def test_cache(self):
        """Test that data is cached"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text("key: value")
            
            manager = TestDataManager()
            manager.data_dir = Path(tmpdir)
            
            # Load first time
            data1 = manager.load_yaml("test.yaml")
            
            # Modify file
            yaml_file.write_text("key: changed")
            
            # Load again - should use cache
            data2 = manager.load_yaml("test.yaml")
            
            assert data1 == data2, "Should use cached data"
    
    def test_clear_cache(self):
        """Test clearing cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text("key: value")
            
            manager = TestDataManager()
            manager.data_dir = Path(tmpdir)
            
            # Load and cache
            manager.load_yaml("test.yaml")
            
            # Clear cache
            manager.clear_cache()
            
            # Modify file
            yaml_file.write_text("key: changed")
            
            # Load again - should load new data
            data = manager.load_yaml("test.yaml")
            
            assert data["key"] == "changed", "Should load new data after cache clear"
