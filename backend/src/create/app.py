import boto3
import os
import json

def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Change "*" to your domain if needed
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    dynamo = boto3.resource("dynamodb").Table(table_name)
    
    # Parse the request body (expected as a JSON string)
    try:
        body = json.loads(event.get("body", "{}"))
    except Exception as e:
        return build_response(400, {
            "status": "error",
            "message": "Invalid request format. Expected JSON in 'body'."
        })
    
    # Check if the payload is an array of items (batch create) or a single item.
    if "items" in body:
        items = body["items"]
        # Validate each item
        for item in items:
            if "id" not in item or "name" not in item or "age" not in item:
                return build_response(400, {
                    "status": "error",
                    "message": "Missing required fields in one or more items: id, name, age"
                })
        # Insert each item into DynamoDB
        try:
            for item in items:
                dynamo.put_item(Item=item)
            return build_response(200, {
                "status": "success",
                "message": "Items created",
                "items": items
            })
        except Exception as e:
            return build_response(500, {
                "status": "error",
                "message": str(e)
            })
    else:
        # Single item processing
        if "id" not in body or "name" not in body or "age" not in body:
            return build_response(400, {
                "status": "error",
                "message": "Missing required fields: id, name, age"
            })
        try:
            dynamo.put_item(Item=body)
            return build_response(200, {
                "status": "success",
                "message": "Item created",
                "item": body
            })
        except Exception as e:
            return build_response(500, {
                "status": "error",
                "message": str(e)
            })
