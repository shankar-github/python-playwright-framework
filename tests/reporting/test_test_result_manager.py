"""
Tests for test result manager
"""
import pytest
from framework.reporting.test_result_manager import TestResultManager, TestStep


class TestTestStep:
    """Tests for TestStep"""
    
    def test_step_initialization(self):
        """Test step initialization"""
        step = TestStep("Test Step")
        
        assert step.name == "Test Step", "Should set name"
        assert step.status == "pending", "Should have default status"
        assert step.data == {}, "Should have empty data by default"
    
    def test_step_with_data(self):
        """Test step with data"""
        step = TestStep("Test Step", data={"key": "value"})
        
        assert step.data == {"key": "value"}, "Should set data"
    
    def test_step_to_dict(self):
        """Test step to_dict conversion"""
        step = TestStep("Test Step", status="passed", data={"key": "value"}, result="success")
        
        step_dict = step.to_dict()
        
        assert step_dict["name"] == "Test Step", "Should include name"
        assert step_dict["status"] == "passed", "Should include status"
        assert step_dict["data"] == {"key": "value"}, "Should include data"
        assert step_dict["result"] == "success", "Should include result"


class TestTestResultManager:
    """Tests for TestResultManager"""
    
    def test_initialization(self):
        """Test manager initialization"""
        manager = TestResultManager("Test Title")
        
        assert manager.test_title == "Test Title", "Should set title"
        assert manager.test_data == {}, "Should have empty test data"
        assert manager.steps == [], "Should have empty steps"
    
    def test_set_title(self):
        """Test setting title"""
        manager = TestResultManager()
        manager.set_title("New Title")
        
        assert manager.test_title == "New Title", "Should set title"
    
    def test_add_test_data(self):
        """Test adding test data"""
        manager = TestResultManager()
        manager.add_test_data("key", "value")
        
        assert manager.test_data["key"] == "value", "Should add test data"
    
    def test_add_test_data_dict(self):
        """Test adding multiple test data items"""
        manager = TestResultManager()
        manager.add_test_data_dict({"key1": "value1", "key2": "value2"})
        
        assert manager.test_data["key1"] == "value1", "Should add first item"
        assert manager.test_data["key2"] == "value2", "Should add second item"
    
    def test_start_step(self):
        """Test starting a step"""
        manager = TestResultManager()
        
        step_index = manager.start_step("Step Name", {"data": "value"})
        
        assert step_index == 0, "Should return step index"
        assert len(manager.steps) == 1, "Should add step"
        assert manager.steps[0].name == "Step Name", "Should set step name"
        assert manager.steps[0].data == {"data": "value"}, "Should set step data"
    
    def test_complete_step(self):
        """Test completing a step"""
        manager = TestResultManager()
        
        step_index = manager.start_step("Step Name")
        manager.complete_step(step_index, status="passed", result="success")
        
        assert manager.steps[0].status == "passed", "Should set status"
        assert manager.steps[0].result == "success", "Should set result"
    
    def test_start_test(self):
        """Test starting test"""
        manager = TestResultManager()
        manager.start_test()
        
        assert manager.start_time is not None, "Should set start time"
    
    def test_end_test(self):
        """Test ending test"""
        manager = TestResultManager()
        manager.start_test()
        manager.end_test("passed")
        
        assert manager.end_time is not None, "Should set end time"
        assert manager.final_result == "passed", "Should set result"
    
    def test_get_summary(self):
        """Test getting summary"""
        manager = TestResultManager("Test Title")
        manager.start_test()
        manager.add_test_data("key", "value")
        manager.start_step("Step 1")
        manager.complete_step(0, status="passed")
        manager.end_test("passed")
        
        summary = manager.get_summary()
        
        assert summary["test_title"] == "Test Title", "Should include title"
        assert summary["test_data"] == {"key": "value"}, "Should include test data"
        assert len(summary["steps"]) == 1, "Should include steps"
        assert summary["final_result"] == "passed", "Should include result"
        assert summary["duration_seconds"] is not None, "Should include duration"
