import boto3
import os
import json
from decimal import Decimal

# Custom JSON encoder for Decimal types (if needed)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Helper function to recursively convert Decimal objects to float
def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def build_response(status_code, body):
    # Convert body to remove any Decimal instances before serializing
    body_converted = convert_decimals(body)
    response = {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Adjust to your domain if needed
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(body_converted, cls=DecimalEncoder)
    }
    print("✅ Final Response:")
    print(json.dumps(response, indent=2, cls=DecimalEncoder))
    return response

def lambda_handler(event, context):
    # Log the full event payload for debugging
    print("🔍 FULL EVENT PAYLOAD:")
    print(json.dumps(event, indent=2, cls=DecimalEncoder))
    
    # Retrieve TABLE_NAME from environment variables
    table_name = os.environ.get("TABLE_NAME")
    print(f"🔧 TABLE_NAME: {table_name}")
    if not table_name:
        error_msg = "TABLE_NAME environment variable is not set."
        print("❌ ERROR:", error_msg)
        return build_response(500, {"status": "error", "message": error_msg})
    
    dynamo = boto3.resource("dynamodb").Table(table_name)
    
    # Parse the request body (expected as a JSON string)
    try:
        body = json.loads(event.get("body", "{}"))
        print("📦 Parsed Body:")
        print(json.dumps(body, indent=2, cls=DecimalEncoder))
    except Exception as e:
        error_msg = f"Invalid request format. Expected JSON in 'body': {str(e)}"
        print("❌ ERROR:", error_msg)
        return build_response(400, {"status": "error", "message": error_msg})
    
    # Validate that the payload contains a "Key" field
    key = body.get("Key")
    if not key:
        error_msg = "Missing Key in payload. Expected payload: {\"Key\": {\"id\": \"123\"}}"
        print("❌ ERROR:", error_msg)
        return build_response(400, {"status": "error", "message": error_msg})
    
    try:
        # Perform the delete operation
        result = dynamo.delete_item(Key=key)
        print("🔍 DynamoDB Delete Result:")
        print(json.dumps(result, indent=2, cls=DecimalEncoder))
        return build_response(200, {"status": "success", "message": "Item deleted"})
    except Exception as e:
        error_msg = f"Error deleting item: {str(e)}"
        print("❌ ERROR:", error_msg)
        return build_response(500, {"status": "error", "message": error_msg})
