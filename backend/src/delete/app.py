import boto3
import os
import json

def lambda_handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    dynamo = boto3.resource("dynamodb").Table(table_name)
    
    # 🛑 Parse the request body (expected as JSON string)
    try:
        body = json.loads(event.get("body", "{}"))
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "status": "error", 
                "message": "Invalid request format. Expected JSON in 'body'."
            })
        }
    
    # 🔍 Validate that the payload contains a "Key" field
    key = body.get("Key")
    if not key:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "status": "error", 
                "message": "Missing Key in payload. Expected payload: {\"Key\": {\"id\": \"123\"}}"
            })
        }
    
    # 🗑️ Delete the item from DynamoDB
    try:
        dynamo.delete_item(Key=key)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success", 
                "message": "Item deleted"
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error", 
                "message": str(e)
            })
        }
