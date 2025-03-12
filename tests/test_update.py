import json
import pytest
import os
import sys
import boto3
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def lambda_context():
    return {}

@pytest.fixture
def event_update():
    return {
        "httpMethod": "PUT",
        "body": json.dumps({"id": "123", "name": "NewName", "age": 35})
    }

@patch("backend.src.update.app.boto3.resource")
def test_update_success(mock_dynamo_resource, event_update, lambda_context):
    mock_table = MagicMock()
    mock_dynamo_resource.return_value.Table.return_value = mock_table
    mock_table.update_item.return_value = {
        "Attributes": {"id": "123", "name": "NewName", "age": 35}
    }

    os.environ["TABLE_NAME"] = "TestTable"

    response = update_app.lambda_handler(event_update, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    assert response_body["updated_item"]["name"] == "NewName"

def test_update_no_table_env(event_update, lambda_context):
    if "TABLE_NAME" in os.environ:
        del os.environ["TABLE_NAME"]

    response = update_app.lambda_handler(event_update, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 500
    assert "TABLE_NAME environment variable is not set." in response["body"]
