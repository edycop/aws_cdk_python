from aws_cdk import core
from aws_cdk import aws_lambda as Lambda
from aws_cdk import aws_apigateway as Apigateway
from aws_cdk import aws_iam as Iam
from aws_cdk import aws_dynamodb as Dynamo
# from aws_cdk import aws_appsync as Appsync


class AwsCdkPythonStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ######## Dynamo DB ###############
        events_table = Dynamo.Table(
            self,
            "events_table",
            table_name='events',
            partition_key=Dynamo.Attribute(
                name="name",
                type=Dynamo.AttributeType.STRING
            ),
            billing_mode=Dynamo.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY  # Don't use in production
        )

        # ######## Lambda Function ###############
        lambda_function = Lambda.Function(
            self,
            'lambda_events',
            code=Lambda.Code.asset('./resources/events'),
            handler='events_info.handler',
            runtime=Lambda.Runtime.PYTHON_3_8,
            description='Lambda function to get information about Python events.',
            environment={
                "EVENTS_TABLE_NAME": events_table.table_name
            }
        )

        # grant permission for reading on Dynamo table
        events_table.grant_read_data(lambda_function)

        events_authorizer = Lambda.Function(
            self,
            'authorizer',
            code=Lambda.Code.asset('./resources/events'),
            handler='authorizer.handler',
            runtime=Lambda.Runtime.PYTHON_3_8,
            description='Authorizer for events endpoint'
        )

        auth_role = Iam.Role(
            self,
            'auth_role_handler',
            assumed_by=Iam.ServicePrincipal("apigateway.amazonaws.com")
        )
        events_authorizer.grant_invoke(auth_role)

        # ######## API Gateway ###############
        api = Apigateway.RestApi(
            self,
            'api_events',
            description='REST API for Python events',
            deploy_options={
                "method_options": {
                    "/*/*": {
                        "throttling_rate_limit": 10,
                        "throttling_burst_limit": 5
                    }
                }
            }
        )

        api_authorizer = Apigateway.CfnAuthorizer(
            self,
            'api_authorizer',
            authorizer_credentials=auth_role.role_arn,
            authorizer_uri=f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{events_authorizer.function_arn}/invocations",
            identity_source="method.request.header.Authorization",
            name="rest-api-authorizer",
            rest_api_id=api.rest_api_id,
            type="REQUEST"
        )

        events_integration = Apigateway.LambdaIntegration(
            lambda_function)
        root_v1 = api.root.add_resource("v1")
        get_events = root_v1.add_resource("events")
        # {URL}/v1/events
        # {URL}/v1/event/{1}

        get_events_method = get_events.add_method(
            "GET",
            events_integration,
            authorization_type=Apigateway.AuthorizationType.CUSTOM
        )
        get_events_method.node.find_child('Resource').add_property_override(
            'AuthorizerId', api_authorizer.ref
        )
