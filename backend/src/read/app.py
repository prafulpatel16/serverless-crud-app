import boto3
import os
import json
from decimal import Decimal

# Custom JSON encoder for handling Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # You can convert to float or str as needed
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    # Log the full event payload for debugging
    print("🔍 FULL EVENT PAYLOAD RECEIVED FROM API GATEWAY:")
    print(json.dumps(event, indent=2))
    
    # Check if 'body' exists in the event and is not None.
    if 'body' in event and event['body'] is not None:
        try:
            payload = json.loads(event['body'])
        except Exception as e:
            error_message = f"Failed to parse JSON from body: {str(e)}"
            print(f"❌ ERROR: {error_message}")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": error_message})
            }
    else:
        payload = event  # Use the event itself as the payload

    # Validate that the payload contains an 'id' field.
    if "id" not in payload:
        error_message = "'id' field is missing in payload!"
        print(f"❌ ERROR: {error_message}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_message})
        }
    
    # Fetch data from DynamoDB based on the provided "id"
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get("TABLE_NAME")
    if not table_name:
        error_message = "TABLE_NAME environment variable is not set."
        print(f"❌ ERROR: {error_message}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }
    
    table = dynamodb.Table(table_name)
    try:
        db_response = table.get_item(Key={"id": payload["id"]})
        if 'Item' in db_response:
            fetched_data = db_response['Item']
        else:
            error_message = f"No record found for id: {payload['id']}"
            print(f"❌ ERROR: {error_message}")
            return {
                "statusCode": 404,
                "body": json.dumps({"error": error_message})
            }
    except Exception as e:
        error_message = f"Error fetching data from DynamoDB: {str(e)}"
        print(f"❌ ERROR: {error_message}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }
    
    # If the HTTP method is GET, display only "name" and "age"
    if event.get("httpMethod", "").upper() == "GET":
        result = {
            "name": fetched_data.get("name"),
            "age": fetched_data.get("age")
        }
        print("📦 FETCHED DATA (GET):")
        print(json.dumps(result, indent=2, cls=DecimalEncoder))
        response = {
            "status": "success",
            "data": result
        }
    else:
        # For non-GET methods, return the full fetched data
        print("📦 FETCHED DATA:")
        print(json.dumps(fetched_data, indent=2, cls=DecimalEncoder))
        response = {
            "status": "success",
            "data": fetched_data
        }
    
    print("✅ SUCCESS:")
    print(json.dumps(response, indent=2, cls=DecimalEncoder))
    
    return {
        "statusCode": 200,
        "body": json.dumps(response, cls=DecimalEncoder)
    }
