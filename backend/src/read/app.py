import boto3
import os
import json
from decimal import Decimal

# Custom JSON encoder for Decimal types
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
    # Convert body first to remove any Decimal instances
    body_converted = convert_decimals(body)
    response = {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Change "*" to your specific domain if needed
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(body_converted, cls=DecimalEncoder)
    }
    # Log the final response
    print("✅ Final Response:")
    print(json.dumps(response, indent=2, cls=DecimalEncoder))
    return response

def lambda_handler(event, context):
    # Log the full event payload for debugging
    print("🔍 FULL EVENT PAYLOAD:")
    print(json.dumps(event, indent=2))
    
    # Retrieve TABLE_NAME from environment variables
    table_name = os.environ.get("TABLE_NAME")
    print(f"🔧 TABLE_NAME: {table_name}")
    if not table_name:
        error_msg = "TABLE_NAME environment variable is not set."
        print(f"❌ ERROR: {error_msg}")
        return build_response(500, {"status": "error", "message": error_msg})
    
    dynamo = boto3.resource("dynamodb").Table(table_name)
    
    # Determine HTTP method
    http_method = event.get("httpMethod", "").upper()
    print(f"🔧 HTTP Method: {http_method}")
    
    if http_method == "GET":
        # Process GET requests using query parameters
        qs = event.get("queryStringParameters", {}) or {}
        print(f"🔧 QueryStringParameters: {json.dumps(qs, indent=2)}")
        id_val = qs.get("id")
        if not id_val:
            error_msg = "Missing 'id' in query parameters"
            print(f"❌ ERROR: {error_msg}")
            return build_response(400, {"status": "error", "message": error_msg})
        
        try:
            print(f"🔍 Fetching item with id: {id_val}")
            db_response = dynamo.get_item(Key={"id": id_val})
            print("🔍 DynamoDB response:")
            print(json.dumps(db_response, indent=2, cls=DecimalEncoder))
            if "Item" in db_response:
                fetched_data = db_response["Item"]
                result = {
                    "name": fetched_data.get("name"),
                    "age": fetched_data.get("age")
                }
                return build_response(200, {"status": "success", "data": result})
            else:
                error_msg = f"No record found for id: {id_val}"
                print(f"❌ ERROR: {error_msg}")
                return build_response(404, {"status": "error", "message": error_msg})
        except Exception as e:
            error_msg = f"Error fetching data from DynamoDB: {str(e)}"
            print(f"❌ ERROR: {error_msg}")
            return build_response(500, {"status": "error", "message": error_msg})
    else:
        error_msg = "Unsupported HTTP method"
        print(f"❌ ERROR: {error_msg}")
        return build_response(400, {"status": "error", "message": error_msg})
