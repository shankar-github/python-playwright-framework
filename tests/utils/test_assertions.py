"""
Tests for assertion utilities
"""
import pytest
from framework.utils.assertions import (
    HardAssertions,
    SoftAssertions,
    hard_assert,
    AssertionError
)


class TestHardAssertions:
    """Tests for hard assertions"""
    
    def test_assert_true(self):
        """Test assert_true"""
        HardAssertions.assert_true(True, "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_true(False, "Should fail")
    
    def test_assert_false(self):
        """Test assert_false"""
        HardAssertions.assert_false(False, "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_false(True, "Should fail")
    
    def test_assert_equal(self):
        """Test assert_equal"""
        HardAssertions.assert_equal(1, 1, "Should pass")
        HardAssertions.assert_equal("test", "test", "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_equal(1, 2, "Should fail")
    
    def test_assert_not_equal(self):
        """Test assert_not_equal"""
        HardAssertions.assert_not_equal(1, 2, "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_not_equal(1, 1, "Should fail")
    
    def test_assert_in(self):
        """Test assert_in"""
        HardAssertions.assert_in(1, [1, 2, 3], "Should pass")
        HardAssertions.assert_in("a", "abc", "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_in(4, [1, 2, 3], "Should fail")
    
    def test_assert_not_in(self):
        """Test assert_not_in"""
        HardAssertions.assert_not_in(4, [1, 2, 3], "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_not_in(1, [1, 2, 3], "Should fail")
    
    def test_assert_is_none(self):
        """Test assert_is_none"""
        HardAssertions.assert_is_none(None, "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_is_none("not none", "Should fail")
    
    def test_assert_is_not_none(self):
        """Test assert_is_not_none"""
        HardAssertions.assert_is_not_none("value", "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_is_not_none(None, "Should fail")
    
    def test_assert_greater_than(self):
        """Test assert_greater_than"""
        HardAssertions.assert_greater_than(5, 3, "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_greater_than(3, 5, "Should fail")
    
    def test_assert_less_than(self):
        """Test assert_less_than"""
        HardAssertions.assert_less_than(3, 5, "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_less_than(5, 3, "Should fail")
    
    def test_assert_contains(self):
        """Test assert_contains"""
        HardAssertions.assert_contains("hello world", "world", "Should pass")

        with pytest.raises(AssertionError):
            HardAssertions.assert_contains("hello", "world", "Should fail")

    def test_assert_string_contains(self):
        """Test assert_string_contains"""
        HardAssertions.assert_string_contains("hello world", "world", "Should pass")

        with pytest.raises(AssertionError):
            HardAssertions.assert_string_contains("hello", "world", "Should fail")
    
    def test_assert_regex(self):
        """Test assert_regex"""
        HardAssertions.assert_regex(r"\d+", "123", "Should pass")
        
        with pytest.raises(AssertionError):
            HardAssertions.assert_regex(r"\d+", "abc", "Should fail")
    
    def test_hard_assert_instance(self):
        """Test hard_assert convenience instance"""
        hard_assert.assert_equal(1, 1, "Should work")
        
        with pytest.raises(AssertionError):
            hard_assert.assert_equal(1, 2, "Should fail")


class TestSoftAssertions:
    """Tests for soft assertions"""
    
    def test_soft_assert_collects_errors(self):
        """Test that soft assertions collect errors"""
        soft = SoftAssertions()
        
        # Add multiple failures
        soft.assert_equal(1, 2, "First failure")
        soft.assert_equal(3, 4, "Second failure")
        soft.assert_true(False, "Third failure")
        
        # Should have 3 errors
        assert len(soft.errors) == 3, "Should collect all errors"
    
    def test_soft_assert_does_not_raise_immediately(self):
        """Test that soft assertions don't raise immediately"""
        soft = SoftAssertions()
        
        # These should not raise
        soft.assert_equal(1, 2, "Should not raise")
        soft.assert_true(False, "Should not raise")
        
        # Errors should be collected
        assert len(soft.errors) == 2, "Errors should be collected"
    
    def test_soft_assert_raises_on_assert_all(self):
        """Test that assert_all raises if there are errors"""
        soft = SoftAssertions()
        
        soft.assert_equal(1, 2, "Failure")
        
        with pytest.raises(AssertionError):
            soft.assert_all()
    
    def test_soft_assert_passes_on_assert_all(self):
        """Test that assert_all passes if no errors"""
        soft = SoftAssertions()
        
        soft.assert_equal(1, 1, "Should pass")
        soft.assert_true(True, "Should pass")
        
        # Should not raise
        soft.assert_all()
    
    def test_soft_assert_all_methods(self):
        """Test all soft assertion methods"""
        soft = SoftAssertions()
        
        soft.assert_true(True, "Should pass")
        soft.assert_false(False, "Should pass")
        soft.assert_equal(1, 1, "Should pass")
        soft.assert_not_equal(1, 2, "Should pass")
        soft.assert_in(1, [1, 2], "Should pass")
        soft.assert_not_in(3, [1, 2], "Should pass")
        soft.assert_is_none(None, "Should pass")
        soft.assert_is_not_none("value", "Should pass")
        soft.assert_greater_than(5, 3, "Should pass")
        soft.assert_less_than(3, 5, "Should pass")
        soft.assert_contains("hello", "ell", "Should pass")
        soft.assert_regex(r"\d+", "123", "Should pass")
        
        # Should not raise
        soft.assert_all()
    
    def test_soft_assert_instance(self):
        """Test soft_assert convenience instance"""
        sa = SoftAssertions()
        sa.assert_equal(1, 1, "Should work")
        
        # Should not raise immediately
        sa.assert_equal(1, 2, "Should collect error")
        
        # Should raise on assert_all
        with pytest.raises(AssertionError):
            sa.assert_all()
