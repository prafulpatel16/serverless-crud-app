import boto3
import os
import json

def lambda_handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    dynamo = boto3.resource("dynamodb").Table(table_name)

    # 🛑 API Gateway sends body as a STRING, so we need to parse it
    try:
        body = json.loads(event["body"])  # ✅ Convert API Gateway body string to JSON
    except (KeyError, TypeError, json.JSONDecodeError):
        return {
            "statusCode": 400,
            "body": json.dumps({"status": "error", "message": "Invalid request format. Expected JSON in 'body'."})
        }

    # 🔍 Ensure required fields are present
    if "id" not in body or "name" not in body or "age" not in body:
        return {
            "statusCode": 400,
            "body": json.dumps({"status": "error", "message": "Missing required fields: id, name, age"})
        }

    # ✅ Insert item into DynamoDB
    try:
        dynamo.put_item(Item=body)
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "success", "message": "Item created", "item": body})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)})
        }
