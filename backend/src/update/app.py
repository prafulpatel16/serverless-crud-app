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
    body_converted = convert_decimals(body)
    response = {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Change "*" to your specific domain if needed
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(body_converted, cls=DecimalEncoder)
    }
    # Log the final response to CloudWatch
    print("✅ Final Response:")
    print(json.dumps(response, indent=2, cls=DecimalEncoder))
    return response

def lambda_handler(event, context):
    print("🔍 FULL EVENT PAYLOAD:")
    print(json.dumps(event, indent=2, cls=DecimalEncoder))
    
    table_name = os.environ.get("TABLE_NAME")
    print(f"🔧 TABLE_NAME: {table_name}")
    if not table_name:
        error_msg = "TABLE_NAME environment variable is not set."
        print("❌ ERROR:", error_msg)
        return build_response(500, {"status": "error", "message": error_msg})
    
    dynamo = boto3.resource("dynamodb").Table(table_name)
    
    http_method = event.get("httpMethod", "").upper()
    print("🔧 HTTP Method:", http_method)
    if http_method != "PUT":
        error_msg = "Unsupported HTTP method. Use PUT."
        print("❌ ERROR:", error_msg)
        return build_response(400, {"status": "error", "message": error_msg})
    
    try:
        payload = json.loads(event.get("body", "{}"))
        print("📦 Parsed Body:")
        print(json.dumps(payload, indent=2, cls=DecimalEncoder))
    except Exception as e:
        error_msg = f"Failed to parse JSON from body: {str(e)}"
        print("❌ ERROR:", error_msg)
        return build_response(400, {"status": "error", "message": error_msg})
    
    if "id" not in payload or not payload["id"]:
        error_msg = "Missing required field: id"
        print("❌ ERROR:", error_msg)
        return build_response(400, {"status": "error", "message": error_msg})
    
    # Check if the payload already contains a pre-built update expression
    if "UpdateExpression" in payload:
        final_expression = payload["UpdateExpression"]
        expression_names = payload.get("ExpressionAttributeNames", {})
        expression_values = payload.get("ExpressionAttributeValues", {})
        print("📝 Using pre-built update expression:")
        print("UpdateExpression:", final_expression)
        print("ExpressionAttributeNames:", expression_names)
        print("ExpressionAttributeValues:", json.dumps(expression_values, cls=DecimalEncoder))
    else:
        # Build update expressions from raw fields (name and/or age)
        update_expressions = []
        expression_names = {}
        expression_values = {}
        if "name" in payload and payload["name"].strip() != "":
            update_expressions.append("#nm = :nm")
            expression_names["#nm"] = "name"
            expression_values[":nm"] = payload["name"].strip()
        if "age" in payload and str(payload["age"]).strip() != "":
            update_expressions.append("#ag = :ag")
            expression_names["#ag"] = "age"
            expression_values[":ag"] = int(payload["age"])
        if not update_expressions:
            error_msg = "No fields to update. Provide at least 'name' or 'age'."
            print("❌ ERROR:", error_msg)
            return build_response(400, {"status": "error", "message": error_msg})
        final_expression = "SET " + ", ".join(update_expressions)
        print("📝 Built Update Expression:", final_expression)
        print("📝 Expression Attribute Names:", expression_names)
        print("📝 Expression Attribute Values:", json.dumps(expression_values, cls=DecimalEncoder))
    
    try:
        result = dynamo.update_item(
            Key={"id": payload["id"]},
            UpdateExpression=final_expression,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW"
        )
        print("🔍 DynamoDB Update Result:")
        print(json.dumps(result, indent=2, cls=DecimalEncoder))
        updated_item = result.get("Attributes", {})
        return build_response(200, {"status": "success", "message": "Item updated", "updated_item": updated_item})
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        print("❌ ERROR:", error_msg)
        return build_response(500, {"status": "error", "message": error_msg})
