# Step Context Manager Guide

## Overview

The step context manager provides a cleaner, more Pythonic way to track test steps compared to manual step variables like `step1`, `step2`, etc.

## Problem with Old Approach

**Before (Manual Step Variables)**:
```python
def test_example(self):
    step1 = self.start_step("Step 1")
    # ... code ...
    self.complete_step(step1, status="passed", result=result)
    
    step2 = self.start_step("Step 2")
    # ... code ...
    self.complete_step(step2, status="passed")
    
    step3 = self.start_step("Step 3")
    # ... code ...
    self.complete_step(step3, status="passed")
```

**Problems**:
- Ugly variable names (step1, step2, step3...)
- Easy to forget to complete steps
- No automatic error handling
- Verbose and repetitive

## Solution: Context Manager

**After (Context Manager)**:
```python
def test_example(self):
    with self.step("Step 1") as step_ctx:
        # ... code ...
        step_ctx.set_result(result)
    
    with self.step("Step 2") as step_ctx:
        # ... code ...
        step_ctx.set_result(result)
    
    with self.step("Step 3") as step_ctx:
        # ... code ...
        step_ctx.set_result(result)
```

**Benefits**:
- Clean, readable code
- Automatic step completion
- Automatic error handling
- No variable name pollution

## Usage Examples

### Basic Usage

```python
def test_basic(self):
    with self.step("Perform action") as step_ctx:
        result = perform_action()
        step_ctx.set_result(result)
```

### With Step Data

```python
def test_with_data(self):
    with self.step("Create user", {"email": "test@example.com"}) as step_ctx:
        user = create_user("test@example.com")
        step_ctx.set_result({"user_id": user.id})
```

### Error Handling

```python
def test_with_error_handling(self):
    with self.step("Risky operation") as step_ctx:
        try:
            result = risky_operation()
            step_ctx.set_result(result)
        except Exception as e:
            step_ctx.set_error(str(e))
            step_ctx.mark_failed()
            raise
```

### Automatic Error Detection

```python
def test_automatic_error(self):
    # If exception occurs, step is automatically marked as failed
    with self.step("Operation that might fail") as step_ctx:
        result = operation_that_might_fail()  # If this raises, step marked as failed
        step_ctx.set_result(result)
```

### Real-World Example

```python
def test_create_user_and_validate(self):
    """Test creating a user via API and validating in database"""
    self.set_test_title("Create User via API and Validate in Database")
    
    # Step 1: Generate test data
    with self.step("Generate test user data") as step_ctx:
        user_data = test_data.generate_user_data()
        self.add_test_data("user_data", user_data)
        step_ctx.set_result(f"Generated user: {user_data['email']}")
    
    # Step 2: Pre-API DB check
    with self.step("Pre-API database validation", {"email": user_data["email"]}) as step_ctx:
        self.db_validator.assert_record_not_exists(
            table_name="users",
            where_clause="email = :email",
            params={"email": user_data["email"]}
        )
        step_ctx.set_result("User does not exist (as expected)")
    
    # Step 3: API call
    with self.step("Create user via POST /users API") as step_ctx:
        response = self.api_client.post("/users", json=user_data)
        user_id = response.json()["id"]
        step_ctx.set_result({"status_code": response.status_code, "user_id": user_id})
    
    # Step 4: Validate response
    with self.step("Validate API response") as step_ctx:
        validator = APIResponseValidator(response)
        validator.assert_status_code(201)
        step_ctx.set_result("Response validation passed")
    
    # Step 5: Post-API DB check
    with self.step("Post-API database validation") as step_ctx:
        self.db_validator.assert_record_exists(
            table_name="users",
            where_clause="id = :id",
            params={"id": user_id}
        )
        step_ctx.set_result("User exists in database")
    
    # Step 6: Cleanup
    with self.step("Cleanup test data") as step_ctx:
        self.api_client.delete(f"/users/{user_id}")
        step_ctx.set_result("Test data cleaned up")
```

## Step Context Methods

### `set_result(result)`
Set the result for the step:
```python
with self.step("Step name") as step_ctx:
    result = perform_action()
    step_ctx.set_result(result)
```

### `set_error(error)`
Set an error for the step:
```python
with self.step("Step name") as step_ctx:
    try:
        result = risky_operation()
    except Exception as e:
        step_ctx.set_error(str(e))
        raise
```

### `mark_failed()`
Explicitly mark step as failed:
```python
with self.step("Step name") as step_ctx:
    if condition_not_met:
        step_ctx.mark_failed()
        step_ctx.set_error("Condition not met")
```

## Automatic Features

1. **Automatic Completion**: Step is automatically completed when exiting the `with` block
2. **Exception Handling**: If an exception occurs, step is automatically marked as failed
3. **Status Tracking**: Status is automatically set based on whether exception occurred

## Migration from Old Pattern

**Old**:
```python
step1 = self.start_step("Step 1")
result = action()
self.complete_step(step1, status="passed", result=result)
```

**New**:
```python
with self.step("Step 1") as step_ctx:
    result = action()
    step_ctx.set_result(result)
```

## Best Practices

1. **Use descriptive step names**: "Create user via API" not "Step 1"
2. **Set results**: Always set result for successful steps
3. **Handle errors**: Use try/except if you need custom error handling
4. **Keep steps focused**: Each step should do one thing
5. **Use step data**: Pass relevant context data when starting steps

## Comparison

| Feature | Old (step1, step2) | New (context manager) |
|---------|-------------------|----------------------|
| Code clarity | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Error handling | Manual | Automatic |
| Step completion | Manual | Automatic |
| Variable pollution | Yes | No |
| Readability | Low | High |
| Maintainability | Medium | High |
