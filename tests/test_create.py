import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Ensure the project root is in sys.path so that backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Create Lambda function code
from backend.src.create import app as create_app

# Define a simple Lambda context fixture
@pytest.fixture
def lambda_context():
    class LambdaContext:
        def __init__(self):
            self.function_name = "TestFunction"
    return LambdaContext()

# Fixture for single item create event
@pytest.fixture
def event_create_single():
    return {
        "body": json.dumps({"id": "123", "name": "TestName", "age": 30})
    }

# Fixture for batch create event
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

# Fixture for missing fields in single item create event
@pytest.fixture
def event_missing_fields():
    return {
        "body": json.dumps({"id": "123", "name": "TestName"})  # Missing 'age'
    }

# Test for successful single item creation
@patch("backend.src.create.app.boto3.resource")
def test_create_single_success(mock_boto_resource, event_create_single, lambda_context):
    # Setup a mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    os.environ["TABLE_NAME"] = "TestTable"

    response = create_app.lambda_handler(event_create_single, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    assert response_body["item"]["id"] == "123"

# Test for successful batch creation
@patch("backend.src.create.app.boto3.resource")
def test_create_batch_success(mock_boto_resource, event_create_batch, lambda_context):
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    os.environ["TABLE_NAME"] = "TestTable"

    response = create_app.lambda_handler(event_create_batch, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    # Expecting two items created
    assert len(response_body["items"]) == 2

# Test for error when required fields are missing (single item)
def test_create_missing_fields(event_missing_fields, lambda_context):
    os.environ["TABLE_NAME"] = "TestTable"
    response = create_app.lambda_handler(event_missing_fields, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert "Missing required fields" in response_body["message"]

# Test for error when TABLE_NAME environment variable is missing
def test_create_no_table_env(event_create_single, lambda_context):
    if "TABLE_NAME" in os.environ:
        del os.environ["TABLE_NAME"]
    response = create_app.lambda_handler(event_create_single, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 500
    assert "TABLE_NAME environment variable is not set." in response_body["message"]
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Ensure the project root is in sys.path so that backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Create Lambda function code
from backend.src.create import app as create_app

# Define a simple Lambda context fixture
@pytest.fixture
def lambda_context():
    class LambdaContext:
        def __init__(self):
            self.function_name = "TestFunction"
    return LambdaContext()

# Fixture for single item create event
@pytest.fixture
def event_create_single():
    return {
        "body": json.dumps({"id": "123", "name": "TestName", "age": 30})
    }

# Fixture for batch create event
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

# Fixture for missing fields in single item create event
@pytest.fixture
def event_missing_fields():
    return {
        "body": json.dumps({"id": "123", "name": "TestName"})  # Missing 'age'
    }

# Test for successful single item creation
@patch("backend.src.create.app.boto3.resource")
def test_create_single_success(mock_boto_resource, event_create_single, lambda_context):
    # Setup a mock DynamoDB Table
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    os.environ["TABLE_NAME"] = "TestTable"

    response = create_app.lambda_handler(event_create_single, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    assert response_body["item"]["id"] == "123"

# Test for successful batch creation
@patch("backend.src.create.app.boto3.resource")
def test_create_batch_success(mock_boto_resource, event_create_batch, lambda_context):
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table
    os.environ["TABLE_NAME"] = "TestTable"

    response = create_app.lambda_handler(event_create_batch, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    # Expecting two items created
    assert len(response_body["items"]) == 2

# Test for error when required fields are missing (single item)
def test_create_missing_fields(event_missing_fields, lambda_context):
    os.environ["TABLE_NAME"] = "TestTable"
    response = create_app.lambda_handler(event_missing_fields, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert "Missing required fields" in response_body["message"]

# Test for error when TABLE_NAME environment variable is missing
def test_create_no_table_env(event_create_single, lambda_context):
    if "TABLE_NAME" in os.environ:
        del os.environ["TABLE_NAME"]
    response = create_app.lambda_handler(event_create_single, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 500
    assert "TABLE_NAME environment variable is not set." in response_body["message"]
