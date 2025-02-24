import boto3
import os

def lambda_handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    dynamo = boto3.resource("dynamodb").Table(table_name)
    
    # Expect payload to include a Key dict, e.g., {"id": "123"}
    key = event.get("payload", {}).get("Key")
    if not key:
        return {"status": "error", "message": "Missing Key in payload"}
    
    try:
        dynamo.delete_item(Key=key)
        return {"status": "success", "message": "Item deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
