import boto3
import os

def lambda_handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    dynamo = boto3.resource("dynamodb").Table(table_name)
    
    try:
        response = dynamo.scan()
        items = response.get("Items", [])
        return {"status": "success", "items": items}
    except Exception as e:
        return {"status": "error", "message": str(e)}
