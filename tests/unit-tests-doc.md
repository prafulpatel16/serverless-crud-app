
# 📚 Unit Testing Documentation for Serverless CRUD App

This document provides a comprehensive guide to unit testing the Serverless CRUD App using Python and pytest. It covers setting up your testing environment, organizing test files, writing tests for individual Lambda functions (Create, Read, Update, Delete), and integrating tests into a CI/CD pipeline.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Test Environment Setup](#test-environment-setup)
3. [Project Structure](#project-structure)
4. [Writing Unit Tests](#writing-unit-tests)
   - [Using pytest](#using-pytest)
   - [Mocking AWS Services](#mocking-aws-services)
5. [Example Test Files](#example-test-files)
   - [Test for Create Function](#test-for-create-function)
   - [Test for Delete Function](#test-for-delete-function)
   - [Test for Read Function](#test-for-read-function)
   - [Test for Update Function](#test-for-update-function)
6. [Running Tests Locally](#running-tests-locally)
7. [Integrating Tests in CI/CD](#integrating-tests-in-cicd)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)
9. [Conclusion](#conclusion)

---

## 1. Introduction

Unit testing is a critical practice that helps ensure your code behaves as expected. In a serverless environment, it is especially important to test your Lambda functions to catch issues early in the development cycle. This guide uses **pytest** as the testing framework and **unittest.mock** for mocking AWS services (like DynamoDB) to avoid actual AWS calls during tests.

---

## 2. Test Environment Setup

### Install Python and Dependencies

Ensure you have Python 3.8 (or later) installed. Install the required testing tools using pip:

```bash
pip install pytest
```

If you use a virtual environment, activate it first:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Directory Structure

Your project should have a structure similar to the following:

```
serverless-crud-app/
├── backend/
│   └── src/
│       ├── create/
│       │   ├── __init__.py
│       │   └── app.py
│       ├── read/
│       │   ├── __init__.py
│       │   └── app.py
│       ├── update/
│       │   ├── __init__.py
│       │   └── app.py
│       └── delete/
│           ├── __init__.py
│           └── app.py
├── tests/
│   ├── __init__.py
│   ├── test_create.py
│   ├── test_read.py
│   ├── test_update.py
│   └── test_delete.py
├── template.yaml
└── README.md
```

> **Note:** Ensure that every folder that needs to be recognized as a package contains an empty `__init__.py` file.

---

## 3. Project Structure

- **backend/src/**: Contains the Lambda function code for each CRUD operation.
- **tests/**: Contains all unit tests. Test files should be named `test_*.py` for pytest to auto-discover them.
- **template.yaml**: SAM/CloudFormation template.
- **README.md**: Project overview and documentation.

---

## 4. Writing Unit Tests

### Using pytest

**pytest** is a popular testing framework that automatically discovers and runs test files and functions. Test functions should be prefixed with `test_`.

### Mocking AWS Services

Since your Lambda functions use `boto3` to interact with AWS, you'll want to mock these calls during tests. Use `unittest.mock` to patch `boto3.resource` calls. This avoids actual AWS calls and lets you simulate various responses.

For example:

```python
from unittest.mock import patch, MagicMock

@patch("backend.src.create.app.boto3.resource")
def test_create_single_success(mock_boto_resource, event_create_single, lambda_context):
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    # Set environment variable for TABLE_NAME
    os.environ["TABLE_NAME"] = "TestTable"
    response = create_app.lambda_handler(event_create_single, lambda_context)
    ...
```

---

## 5. Example Test Files

### Test for Create Function (`tests/test_create.py`)

```python
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path so backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.create import app as create_app

@pytest.fixture
def lambda_context():
    class LambdaContext:
        function_name = "TestCreateFunction"
    return LambdaContext()

@pytest.fixture
def event_create_single():
    return {
        "body": json.dumps({"id": "123", "name": "TestName", "age": 30})
    }

@pytest.fixture
def event_create_batch():
    return {
        "body": json.dumps({
            "items": [
                {"id": "abc", "name": "Batch1", "age": 25},
                {"id": "def", "name": "Batch2", "age": 40}
            ]
        })
    }

@pytest.fixture
def event_missing_fields():
    return {
        "body": json.dumps({"id": "123", "name": "TestName"})  # Missing 'age'
    }

@patch("backend.src.create.app.boto3.resource")
def test_create_single_success(mock_boto_resource, event_create_single, lambda_context):
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    os.environ["TABLE_NAME"] = "TestTable"
    response = create_app.lambda_handler(event_create_single, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    assert response_body["item"]["id"] == "123"

@patch("backend.src.create.app.boto3.resource")
def test_create_batch_success(mock_boto_resource, event_create_batch, lambda_context):
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    os.environ["TABLE_NAME"] = "TestTable"
    response = create_app.lambda_handler(event_create_batch, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    assert len(response_body["items"]) == 2

def test_create_no_table_env(event_create_single, lambda_context):
    os.environ.pop("TABLE_NAME", None)
    response = create_app.lambda_handler(event_create_single, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert "TABLE_NAME environment variable is not set." in response_body["message"]

def test_create_missing_fields(event_missing_fields, lambda_context):
    os.environ["TABLE_NAME"] = "TestTable"
    response = create_app.lambda_handler(event_missing_fields, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert "Missing required fields" in response_body["message"]
```

---

### Test for Delete Function (`tests/test_delete.py`)

```python
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.delete import app as delete_app

@pytest.fixture
def lambda_context():
    class LambdaContext:
        function_name = "TestDeleteFunction"
    return LambdaContext()

@pytest.fixture
def event_delete():
    return {
        "body": json.dumps({"Key": {"id": "123"}})
    }

@patch("backend.src.delete.app.boto3.resource")
def test_delete_success(mock_boto_resource, event_delete, lambda_context):
    mock_table = MagicMock()
    # Simulate a successful delete
    mock_table.delete_item.return_value = {}
    mock_boto_resource.return_value.Table.return_value = mock_table
    os.environ["TABLE_NAME"] = "TestTable"
    response = delete_app.lambda_handler(event_delete, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    assert "Item deleted" in response_body["message"]

def test_delete_no_table_env(event_delete, lambda_context):
    os.environ.pop("TABLE_NAME", None)
    response = delete_app.lambda_handler(event_delete, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert "TABLE_NAME environment variable is not set." in response_body["message"]
```

---

### Test for Read Function (`tests/test_read.py`)

```python
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.read import app as read_app

@pytest.fixture
def lambda_context():
    class LambdaContext:
        function_name = "TestReadFunction"
    return LambdaContext()

@pytest.fixture
def event_read():
    return {
        "httpMethod": "GET",
        "queryStringParameters": {"id": "123"}
    }

@patch("backend.src.read.app.boto3.resource")
def test_read_success(mock_boto_resource, event_read, lambda_context):
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    # Simulate a DynamoDB response with an item
    mock_table.get_item.return_value = {"Item": {"id": "123", "name": "TestName", "age": 30}}
    os.environ["TABLE_NAME"] = "TestTable"
    response = read_app.lambda_handler(event_read, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    assert response_body["data"]["name"] == "TestName"

def test_read_unsupported_method(lambda_context):
    event = {
        "httpMethod": "POST",
        "queryStringParameters": {"id": "123"}
    }
    os.environ["TABLE_NAME"] = "TestTable"
    response = read_app.lambda_handler(event, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 400
    assert "Unsupported HTTP method" in response_body["message"]
```

---

### Test for Update Function (`tests/test_update.py`)

```python
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.update import app as update_app

@pytest.fixture
def lambda_context():
    class LambdaContext:
        function_name = "TestUpdateFunction"
    return LambdaContext()

@pytest.fixture
def event_update():
    return {
        "httpMethod": "PUT",
        "body": json.dumps({"id": "123", "name": "NewName", "age": 35})
    }

@patch("backend.src.update.app.boto3.resource")
def test_update_success(mock_boto_resource, event_update, lambda_context):
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    # Simulate successful update
    mock_table.update_item.return_value = {"Attributes": {"id": "123", "name": "NewName", "age": 35}}
    os.environ["TABLE_NAME"] = "TestTable"
    response = update_app.lambda_handler(event_update, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    assert response_body["updated_item"]["name"] == "NewName"

def test_update_no_table_env(event_update, lambda_context):
    os.environ.pop("TABLE_NAME", None)
    response = update_app.lambda_handler(event_update, lambda_context)
    response_body = json.loads(response["body"])
    assert response["statusCode"] == 500
    assert "TABLE_NAME environment variable is not set." in response_body["message"]
```

---

## 6. Running Tests Locally

1. **Install pytest:**

   ```bash
   pip install pytest
   ```

2. **Run Tests from the Project Root:**

   ```bash
   cd /mnt/c/devops-work/serverless-crud-app
   pytest tests/
   ```

This will discover and execute all test files in the `tests/` directory.

---

## 7. Integrating Tests in CI/CD

### GitHub Actions

Create a `.github/workflows/ci.yaml` file with the following content:

```yaml
name: CI

on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          pip install pytest
          # If you have a requirements.txt, run:
          # pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest tests/
```

This workflow will run your tests on every push or pull request, ensuring your code remains stable.

---

## 8. Troubleshooting Common Issues

- **ModuleNotFoundError:**  
  Ensure you have added the project root to `sys.path` at the top of each test file and that you have `__init__.py` files in the appropriate directories.

- **Environment Variables:**  
  Confirm that your tests set `TABLE_NAME` where required. Use `os.environ["TABLE_NAME"] = "TestTable"` in your test functions or fixtures.

- **Mocking AWS Services:**  
  Use the `@patch` decorator from `unittest.mock` to simulate `boto3.resource` calls and avoid real AWS calls during testing.

---

## 9. Conclusion

By following this guide, you can set up a comprehensive unit testing framework for your Serverless CRUD App using pytest. This ensures that your Lambda functions for Create, Read, Update, and Delete operations are well-tested locally in VS Code and integrated into your CI/CD pipeline for automated testing during deployments.

Happy testing and coding!

---
```
You can use the [pytest-html](https://pypi.org/project/pytest-html/) plugin to generate an HTML report. Here’s how:

1. **Install pytest-html:**

   ```bash
   pip install pytest-html
   ```

2. **Run your tests with HTML reporting:**

   From your project root, run:

   ```bash
   pytest --html=report.html --self-contained-html
   ```

   This command will run your tests and produce a `report.html` file that you can open in any browser. The `--self-contained-html` flag makes sure that the report is standalone (all CSS/JS embedded).

3. **View the Report:**

   Open `report.html` in your browser to see the test results in a nicely formatted HTML report.

You can also integrate this into your CI/CD pipeline by storing or publishing the HTML report as an artifact.

Happy testing!