import json


def handler(event: dict, context) -> dict:
    print(f'eventAuthorizer: {json.dumps(event)}')
    auth = event['headers']['Authorization']
    print(f'auth: {auth}')

    if auth == 'LtIfelBlD4P938JxeftTNxBM4vn4h2mr':
        return build_response(event)
    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'text/plain'
        },
        'body': 'Not authorized'
    }


def build_response(request):
    return {
        "principalId": request['requestContext']['identity']['principalOrgId'],
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": request['methodArn']
                }
            ]
        },
    }
