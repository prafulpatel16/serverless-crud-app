import boto3
import os
import json
from decimal import Decimal

# Custom JSON encoder for handling Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    dynamo = boto3.resource("dynamodb").Table(table_name)

    # 🛑 API Gateway sends the body as a STRING, so we need to parse it
    try:
        body = json.loads(event["body"])
    except (KeyError, TypeError, json.JSONDecodeError):
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"status": "error", "message": "Invalid request format. Expected JSON in 'body'."}
            )
        }

    # 🔍 Ensure the "id" field is present (needed to identify which item to update)
    if "id" not in body:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"status": "error", "message": "Missing required field: id"}
            )
        }

    # Prepare partial update expressions for any fields present (e.g., name, age)
    update_expressions = []
    expression_values = {}
    expression_names = {}

    # If "name" is provided, include it in the update
    if "name" in body:
        update_expressions.append("#n = :n")
        expression_names["#n"] = "name"
        expression_values[":n"] = body["name"]

    # If "age" is provided, include it in the update
    if "age" in body:
        update_expressions.append("#a = :a")
        expression_names["#a"] = "age"
        expression_values[":a"] = body["age"]

    # If no fields to update were passed in, return an error
    if not update_expressions:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"status": "error", "message": "No fields to update."}
            )
        }

    # Construct the final UpdateExpression
    final_expression = "SET " + ", ".join(update_expressions)

    # Perform the DynamoDB update
    try:
        result = dynamo.update_item(
            Key={"id": body["id"]},
            UpdateExpression=final_expression,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW"  # Return the updated item attributes
        )

        updated_item = result.get("Attributes", {})

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "message": "Item updated",
                "updated_item": updated_item
            }, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"status": "error", "message": str(e)},
                cls=DecimalEncoder
            )
        }
