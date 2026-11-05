import json
import os
import uuid
from decimal import Decimal, InvalidOperation

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ.get("TABLE_NAME", "HealthLog"))

# date + fasting sugar, after-meal sugar, systolic, diastolic, weight
READINGS = ["fs", "pm", "sys", "dia", "wt"]


def to_json(o):
    # DynamoDB returns numbers as Decimal; turn them back into int/float
    if isinstance(o, Decimal):
        return int(o) if o == o.to_integral_value() else float(o)
    return str(o)


def respond(code, body):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=to_json),
    }


def clean(data):
    """Validate the request body and return the item to store."""
    date = str(data.get("date", ""))[:10]
    if len(date) != 10:
        raise ValueError("date is required (YYYY-MM-DD)")
    item = {"date": date}
    for field in READINGS:
        value = data.get(field)
        if value is not None:
            try:
                item[field] = Decimal(str(value))
            except InvalidOperation:
                raise ValueError(f"{field} must be a number")
    if len(item) == 1:
        raise ValueError("enter at least one reading")
    if ("sys" in item) != ("dia" in item):
        raise ValueError("enter both systolic and diastolic, or neither")
    return item


def lambda_handler(event, context):
    # The Cognito authorizer on API Gateway puts the signed-in user's id here
    try:
        user = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    except KeyError:
        return respond(401, {"error": "unauthorized"})

    method = event["requestContext"]["http"]["method"]
    entry_id = (event.get("pathParameters") or {}).get("id")

    try:
        if method == "GET":
            result = table.query(KeyConditionExpression=Key("userId").eq(user))
            return respond(200, result["Items"])

        data = json.loads(event.get("body") or "{}", parse_float=Decimal)

        if method == "POST":
            item = clean(data)
            item["userId"] = user
            item["entryId"] = f"{item['date']}_{uuid.uuid4().hex[:8]}"
            table.put_item(Item=item)
            return respond(201, item)

        if method == "PUT" and entry_id:
            item = clean(data)
            item["userId"] = user
            item["entryId"] = entry_id
            table.put_item(Item=item, ConditionExpression="attribute_exists(userId)")
            return respond(200, item)

        if method == "DELETE" and entry_id:
            table.delete_item(Key={"userId": user, "entryId": entry_id})
            return respond(200, {"deleted": entry_id})

        return respond(404, {"error": "route not found"})

    except ValueError as err:  # bad input (includes invalid JSON)
        return respond(400, {"error": str(err)})
    except ClientError as err:
        if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return respond(404, {"error": "entry not found"})
        raise