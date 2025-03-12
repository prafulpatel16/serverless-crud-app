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
def event_read():
    return {
        "httpMethod": "GET",
        "queryStringParameters": {"id": "123"}
    }

@patch("backend.src.read.app.boto3.resource")
def test_read_success(mock_dynamo_resource, event_read, lambda_context):
    mock_table = MagicMock()
    mock_dynamo_resource.return_value.Table.return_value = mock_table
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
    assert response_body["message"] == "Unsupported HTTP method"
