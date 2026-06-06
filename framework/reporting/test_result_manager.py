"""
Test Result Manager for customizing test results with title, steps, data, and results
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import allure
from framework.core.logger import log
from framework.utils.redact import redact_dict, redact_value, redact_payload


class TestStep:
    """Represents a single test step"""
    
    def __init__(self, name: str, status: str = "pending", data: Optional[Dict[str, Any]] = None, 
                 result: Optional[Any] = None, error: Optional[str] = None):
        self.name = name
        self.status = status  # pending, passed, failed, skipped
        self.data = data or {}
        self.result = result
        self.error = error
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        # Safely serialize result
        result_str = None
        if self.result is not None:
            try:
                if isinstance(self.result, (dict, list, str, int, float, bool, type(None))):
                    result_str = self.result
                else:
                    result_str = str(self.result)
            except Exception:
                result_str = str(self.result)
        
        return {
            "name": self.name,
            "status": self.status,
            "data": self.data,
            "result": result_str,
            "error": self.error,
            "timestamp": self.timestamp
        }


class TestResultManager:
    """Manages test results with title, steps, data, and results"""
    
    def __init__(self, test_title: str = ""):
        self.test_title = test_title
        self.test_data: Dict[str, Any] = {}
        self.steps: List[TestStep] = []
        self.final_result: Optional[str] = None
        self.error_message: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def set_title(self, title: str):
        """Set test title"""
        self.test_title = title
        allure.dynamic.title(title)

    def has_failed_steps(self) -> bool:
        """Return True if any recorded step failed."""
        return any(step.status == "failed" for step in self.steps)
        log.debug(f"Test title set: {title}")
    
    def add_test_data(self, key: str, value: Any):
        """Add test data with sensitive value redaction."""
        safe_value = redact_value(key, value)
        self.test_data[key] = safe_value
        log.debug(f"Test data added: {key} = {safe_value}")

    def add_test_data_dict(self, data: Dict[str, Any]):
        """Add multiple test data items with redaction."""
        safe_data = redact_dict(data)
        self.test_data.update(safe_data)
        log.debug(f"Test data updated: {safe_data}")

    def start_step(self, step_name: str, step_data: Optional[Dict[str, Any]] = None) -> int:
        """Start a new test step and return step index."""
        step = TestStep(name=step_name, status="pending", data=redact_dict(step_data or {}))
        step_index = len(self.steps)
        self.steps.append(step)
        log.info(f"Step started: {step_name}")
        return step_index
    
    def complete_step(self, step_index: int, status: str = "passed", result: Optional[Any] = None, 
                      error: Optional[str] = None):
        """Complete a test step"""
        if 0 <= step_index < len(self.steps):
            step = self.steps[step_index]
            step.status = status
            step.result = result
            step.error = error
            
            log.info(f"Step completed: {step.name} - {status}")
            
            # Attach result to Allure if available
            if result is not None:
                try:
                    safe_result = redact_payload(result)
                    if isinstance(safe_result, (dict, list)):
                        allure.attach(
                            json.dumps(safe_result, indent=2, default=str),
                            name=f"{step.name} - Result",
                            attachment_type=allure.attachment_type.JSON
                        )
                    else:
                        allure.attach(
                            str(safe_result),
                            name=f"{step.name} - Result",
                            attachment_type=allure.attachment_type.TEXT
                        )
                except Exception:
                    # Silently ignore attachment failures - not critical for test execution
                    log.warning(f"Failed to attach step result to Allure: {step.name}")
            
            if error:
                allure.attach(
                    error,
                    name=f"{step.name} - Error",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    def start_test(self):
        """Mark test as started"""
        self.start_time = datetime.now()
        log.info(f"Test started: {self.test_title}")
    
    def end_test(self, result: str, error_message: Optional[str] = None):
        """Mark test as ended with result"""
        self.end_time = datetime.now()
        self.final_result = result
        self.error_message = error_message
        
        # Calculate duration
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        log.info(f"Test ended: {self.test_title} - {result}")
        
        # Attach comprehensive test result to Allure
        self._attach_test_result_to_allure(duration)
    
    def _attach_test_result_to_allure(self, duration: Optional[float] = None):
        """Attach complete test result to Allure report"""
        # Set test title
        if self.test_title:
            allure.dynamic.title(self.test_title)
        
        # Create comprehensive test result summary
        result_summary = {
            "test_title": self.test_title,
            "test_data": redact_dict(self.test_data),
            "steps": [step.to_dict() for step in self.steps],
            "final_result": self.final_result,
            "error_message": self.error_message,
            "duration_seconds": duration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
        
        # Attach as JSON (with safe serialization)
        try:
            allure.attach(
                json.dumps(result_summary, indent=2, default=str),
                name="Test Result Summary",
                attachment_type=allure.attachment_type.JSON
            )
        except (TypeError, ValueError) as e:
            # Fallback to text if JSON serialization fails
            allure.attach(
                str(result_summary),
                name="Test Result Summary",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # Create HTML summary
        html_summary = self._create_html_summary(result_summary, duration)
        allure.attach(
            html_summary,
            name="Test Result Summary (HTML)",
            attachment_type=allure.attachment_type.HTML
        )
        
        # Attach test data separately
        if self.test_data:
            try:
                allure.attach(
                    json.dumps(self.test_data, indent=2, default=str),
                    name="Test Data",
                    attachment_type=allure.attachment_type.JSON
                )
            except (TypeError, ValueError):
                allure.attach(
                    str(self.test_data),
                    name="Test Data",
                    attachment_type=allure.attachment_type.TEXT
                )
        
        # Attach steps summary
        if self.steps:
            steps_summary = {
                "total_steps": len(self.steps),
                "passed_steps": len([s for s in self.steps if s.status == "passed"]),
                "failed_steps": len([s for s in self.steps if s.status == "failed"]),
                "steps": [step.to_dict() for step in self.steps]
            }
            try:
                allure.attach(
                    json.dumps(steps_summary, indent=2, default=str),
                    name="Test Steps Summary",
                    attachment_type=allure.attachment_type.JSON
                )
            except (TypeError, ValueError):
                allure.attach(
                    str(steps_summary),
                    name="Test Steps Summary",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    def _create_html_summary(self, result_summary: Dict[str, Any], duration: Optional[float]) -> str:
        """Create HTML summary of test result"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 15px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .test-data {{ background-color: #f9f9f9; padding: 10px; border-radius: 3px; }}
                .step {{ margin: 10px 0; padding: 10px; border-left: 4px solid #2196F3; }}
                .step.passed {{ border-left-color: #4CAF50; }}
                .step.failed {{ border-left-color: #f44336; }}
                .step.pending {{ border-left-color: #ff9800; }}
                .result {{ font-weight: bold; font-size: 18px; }}
                .result.passed {{ color: #4CAF50; }}
                .result.failed {{ color: #f44336; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{result_summary['test_title']}</h1>
            </div>
            
            <div class="section">
                <h2>Test Result</h2>
                <p class="result {result_summary['final_result']}">
                    Status: {result_summary['final_result'].upper()}
                </p>
                {f'<p>Duration: {duration:.2f} seconds</p>' if duration else ''}
                {f'<p style="color: #f44336;">Error: {result_summary["error_message"]}</p>' if result_summary.get('error_message') else ''}
            </div>
            
            <div class="section">
                <h2>Test Data</h2>
                <div class="test-data">
                    <pre>{json.dumps(result_summary['test_data'], indent=2)}</pre>
                </div>
            </div>
            
            <div class="section">
                <h2>Test Steps ({len(result_summary['steps'])} total)</h2>
        """
        
        for step in result_summary['steps']:
            html += f"""
                <div class="step {step['status']}">
                    <h3>{step['name']} - {step['status'].upper()}</h3>
                    {f'<p><strong>Data:</strong> {json.dumps(step["data"], indent=2)}</p>' if step.get('data') else ''}
                    {f'<p><strong>Result:</strong> {step["result"]}</p>' if step.get('result') else ''}
                    {f'<p style="color: #f44336;"><strong>Error:</strong> {step["error"]}</p>' if step.get('error') else ''}
                    <p><small>Timestamp: {step["timestamp"]}</small></p>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test result summary"""
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "test_title": self.test_title,
            "test_data": redact_dict(self.test_data),
            "steps": [step.to_dict() for step in self.steps],
            "final_result": self.final_result,
            "error_message": self.error_message,
            "duration_seconds": duration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
