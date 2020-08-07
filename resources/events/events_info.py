import json
import os

import boto3
from botocore.exceptions import ClientError
# from boto3.dynamodb.conditions import Key, Attr


EVENTS_TABLE_NAME = os.getenv("EVENTS_TABLE_NAME")


def handler(event, context):
    print(f'event: {json.dumps(event)}')

    return query_dynamo()

    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'text/plain'
        },
        'body': 'Python Colombia'
    }


def query_dynamo() -> dict:
    try:
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(EVENTS_TABLE_NAME)
        response = {"Not data"}
        params = {"TableName": EVENTS_TABLE_NAME}
        response = table.scan(params)
        print(f"response with parameters: {response}")
        if response['Items'] != None:
            return {
                "statusCode": 200,
                "headers": {
                    'Content-Type': 'text/plain'
                },
                'body': json.dumps(response['Items'])
            }
        else:
            return {
                "statusCode": 200,
                "headers": {
                    'Content-Type': 'text/plain'
                },
                'body': json.dumps(response)
            }
    except ClientError as err:
        print(f"ERROR, query to DynamoDB: {err}")
        return {
            "statusCode": 500,
            "headers": {
                'Content-Type': 'text/plain'
            },
            'body': json.dumps(err.response['Error'])
        }
