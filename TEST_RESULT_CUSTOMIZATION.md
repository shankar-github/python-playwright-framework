# Test Result Customization Guide

## Overview

The framework provides comprehensive test result customization that captures:
1. **Test Title** - Custom test titles
2. **Test Steps** - Detailed step-by-step execution
3. **Test Data** - All test data used during execution
4. **Test Results** - Final result with detailed information

## Features

### 1. Test Title Customization

Set custom test titles that appear in Allure reports:

```python
def test_example(self):
    self.set_test_title("Custom Test Title")
    # ... test code ...
```

### 2. Test Data Tracking

Track all test data used during test execution:

```python
def test_example(self):
    # Add single data item
    self.add_test_data("user_email", "test@example.com")
    
    # Add multiple data items
    self.add_test_data_dict({
        "user_id": 123,
        "user_name": "John Doe",
        "user_role": "admin"
    })
```

### 3. Test Steps Tracking

Track detailed test steps with data and results:

```python
def test_example(self):
    # Start a step
    step1 = self.start_step("Step Name", {"data": "value"})
    
    # Perform actions
    result = perform_action()
    
    # Complete the step
    self.complete_step(step1, status="passed", result=result)
```

### 4. Complete Test Result

The framework automatically captures:
- Test title
- All test data
- All test steps with status, data, and results
- Final test result (passed/failed)
- Error messages (if failed)
- Test duration
- Timestamps

## Usage Examples

### Example 1: API Test with Steps

```python
@pytest.mark.api
def test_create_user(self):
    """Test creating a user via API"""
    # Set test title
    self.set_test_title("Create User via API")
    
    # Step 1: Generate test data
    step1 = self.start_step("Generate test user data")
    user_data = test_data.generate_user_data()
    self.add_test_data("user_data", user_data)
    self.complete_step(step1, status="passed", result=user_data)
    
    # Step 2: Create user via API
    step2 = self.start_step("Create user via API", {"endpoint": "/users"})
    response = self.api_client.post("/users", json=user_data)
    response_data = response.json()
    self.complete_step(step2, status="passed", result=response_data)
    
    # Step 3: Validate response
    step3 = self.start_step("Validate API response")
    validator = APIResponseValidator(response)
    validator.assert_status_code(201)
    self.complete_step(step3, status="passed", result="Validation passed")
```

### Example 2: Web UI Test with Steps

```python
@pytest.mark.web
def test_user_login(self):
    """Test user login flow"""
    # Set test title
    self.set_test_title("User Login Flow")
    
    # Add test data
    credentials = {"email": "test@example.com", "password": "pass123"}
    self.add_test_data("credentials", credentials)
    
    # Step 1: Navigate to login page
    step1 = self.start_step("Navigate to login page")
    self.page.navigate("/login")
    self.complete_step(step1, status="passed", result="Page loaded")
    
    # Step 2: Enter credentials
    step2 = self.start_step("Enter credentials")
    self.page.fill("#email", credentials["email"])
    self.page.fill("#password", credentials["password"])
    self.complete_step(step2, status="passed", result="Credentials entered")
    
    # Step 3: Submit login
    step3 = self.start_step("Submit login form")
    self.page.click("button[type='submit']")
    self.complete_step(step3, status="passed", result="Form submitted")
```

### Example 3: Database Test with Steps

```python
@pytest.mark.db
def test_data_integrity(self):
    """Test database data integrity"""
    # Set test title
    self.set_test_title("Database Data Integrity Check")
    
    # Step 1: Setup test data
    step1 = self.start_step("Setup test data")
    test_data = {"name": "Test", "value": 100}
    self.db_client.execute_update("INSERT INTO test_table ...", test_data)
    self.complete_step(step1, status="passed", result="Data inserted")
    
    # Step 2: Validate data
    step2 = self.start_step("Validate data integrity")
    result = self.db_validator.assert_record_exists(...)
    self.complete_step(step2, status="passed", result="Integrity check passed")
```

## Allure Report Output

The test result customization automatically generates:

### 1. Test Result Summary (JSON)
- Complete test information in JSON format
- Includes all steps, data, and results

### 2. Test Result Summary (HTML)
- Beautiful HTML summary with:
  - Test title
  - Test result status
  - Test duration
  - Test data table
  - Step-by-step execution details
  - Color-coded status indicators

### 3. Test Data Attachment
- All test data as JSON attachment
- Easy to view and analyze

### 4. Test Steps Summary
- Summary of all steps
- Passed/failed step counts
- Detailed step information

## Step Status Values

- `"passed"` - Step completed successfully
- `"failed"` - Step failed
- `"skipped"` - Step was skipped
- `"pending"` - Step is pending execution

## Best Practices

1. **Always set test title** - Makes reports more readable
   ```python
   self.set_test_title("Descriptive Test Title")
   ```

2. **Track important test data** - Helps with debugging
   ```python
   self.add_test_data("key", value)
   ```

3. **Use steps for major actions** - Break down test into logical steps
   ```python
   step = self.start_step("Action Description", {"context": "data"})
   # ... perform action ...
   self.complete_step(step, status="passed", result=result)
   ```

4. **Include step data** - Provide context for each step
   ```python
   self.start_step("Step Name", {"input": value, "expected": result})
   ```

5. **Capture step results** - Store important results
   ```python
   self.complete_step(step, status="passed", result={"id": 123, "status": "created"})
   ```

## Viewing Results

### Allure Report
```bash
# Generate report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

In the Allure report, you'll see:
- **Test Title** in the test name
- **Test Steps** in the "Steps" tab
- **Test Data** in attachments
- **Test Result Summary** in attachments (JSON and HTML)

### Console Output
Test steps and data are also logged to console for immediate feedback.

## Advanced Usage

### Error Handling in Steps

```python
step = self.start_step("Risky Operation")
try:
    result = risky_operation()
    self.complete_step(step, status="passed", result=result)
except Exception as e:
    self.complete_step(step, status="failed", error=str(e))
    raise
```

### Conditional Steps

```python
if condition:
    step = self.start_step("Conditional Step")
    # ... perform action ...
    self.complete_step(step, status="passed")
```

### Nested Steps (via Allure)

```python
with allure.step("Parent Step"):
    step1 = self.start_step("Child Step 1")
    # ... action ...
    self.complete_step(step1, status="passed")
    
    with allure.step("Nested Child"):
        step2 = self.start_step("Child Step 2")
        # ... action ...
        self.complete_step(step2, status="passed")
```

## Integration with Existing Tests

The test result customization is automatically available in all tests that inherit from `BaseTest`. No additional setup required!

Simply use the methods:
- `self.set_test_title()`
- `self.add_test_data()`
- `self.start_step()`
- `self.complete_step()`

The framework handles the rest automatically.
