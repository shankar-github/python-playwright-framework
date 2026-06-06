"""
Test data cleanup registry for guaranteed cleanup
"""
from typing import Dict, List, Callable, Any, Optional
from framework.core.logger import log
import uuid


class TestDataCleanupRegistry:
    """Registry to track test data for guaranteed cleanup"""
    
    def __init__(self):
        self.cleanup_tasks: List[Dict[str, Any]] = []
        self.test_id: Optional[str] = None
    
    def register_cleanup(
        self,
        cleanup_func: Callable,
        *args,
        description: str = "",
        **kwargs
    ):
        """Register a cleanup function to be called on test completion
        
        Args:
            cleanup_func: Function to call for cleanup
            *args: Arguments to pass to cleanup function
            description: Description of what is being cleaned up
            **kwargs: Keyword arguments to pass to cleanup function
        """
        task = {
            "func": cleanup_func,
            "args": args,
            "kwargs": kwargs,
            "description": description,
            "executed": False
        }
        self.cleanup_tasks.append(task)
        log.debug(f"Registered cleanup task: {description}")
    
    def execute_cleanup(self):
        """Execute all registered cleanup tasks"""
        log.info(f"Executing {len(self.cleanup_tasks)} cleanup tasks")
        
        # Execute in reverse order (LIFO)
        for task in reversed(self.cleanup_tasks):
            if not task["executed"]:
                try:
                    log.debug(f"Executing cleanup: {task['description']}")
                    task["func"](*task["args"], **task["kwargs"])
                    task["executed"] = True
                    log.debug(f"Cleanup completed: {task['description']}")
                except Exception as e:
                    log.error(f"Cleanup failed for {task['description']}: {str(e)}")
                    # Continue with other cleanup tasks even if one fails
        
        self.cleanup_tasks.clear()
        log.info("All cleanup tasks executed")
    
    def clear(self):
        """Clear all registered cleanup tasks"""
        self.cleanup_tasks.clear()
        log.debug("Cleanup registry cleared")


# Global registry instance
cleanup_registry = TestDataCleanupRegistry()
