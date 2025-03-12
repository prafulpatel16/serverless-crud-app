import json
import os
import pytest
from unittest.mock import patch, MagicMock
from backend.src.delete import app as delete_app

@pytest.fixture
def lambda_context():
    return {}

@pytest.fixture
def event_delete():
    return {
        "body": json.dumps({"Key": {"id": "123"}})
    }

@patch("backend.src.delete.app.boto3.resource")
def test_delete_success(mock_dynamo_resource, event_delete, lambda_context):
    mock_table = MagicMock()
    mock_dynamo_resource.return_value.Table.return_value = mock_table

    os.environ["TABLE_NAME"] = "TestTable"

    response = delete_app.lambda_handler(event_delete, lambda_context)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["status"] == "success"
    assert "Item deleted" in response_body["message"]

def test_delete_missing_table_env(event_delete, lambda_context):
    if "TABLE_NAME" in os.environ:
        del os.environ["TABLE_NAME"]

    response = delete_app.lambda_handler(event_delete, lambda_context)
    assert response["statusCode"] == 500
    assert "TABLE_NAME environment variable is not set." in response["body"]
