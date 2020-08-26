import boto3
import json
import os

# Global variables are reused across execution contexts (if available)
session = boto3.Session()


def lambda_handler(event, context):
    """
        AWS Lambda handler
        Parameters
        ----------
        context: object, required
            Lambda Context runtime methods and attributes

        Attributes
        ----------

        context.aws_request_id: str
            Lambda request ID
        context.client_context: object
            Additional context when invoked through AWS Mobile SDK
        context.function_name: str
            Lambda function name
        context.function_version: str
            Function version identifier
        context.get_remaining_time_in_millis: function
            Time in milliseconds before function times out
        context.identity:
            Cognito identity provider context when invoked through AWS Mobile SDK
        context.invoked_function_arn: str
            Function ARN
        context.log_group_name: str
            Cloudwatch Log group name
        context.log_stream_name: str
            Cloudwatch Log stream name
        context.memory_limit_in_mb: int
            Function memory

            https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

        event: dict, required
        
            API Gateway Lambda Proxy Input Format

            {
                "resource": "Resource path",
                "path": "Path parameter",
                "httpMethod": "Incoming request's method name"
                "headers": {Incoming request headers}
                "queryStringParameters": {query string parameters }
                "pathParameters":  {path parameters}
                "stageVariables": {Applicable stage variables}
                "requestContext": {Request context, including authorizer-returned key-value pairs}
                "body": "A JSON string of the request payload."
                "isBase64Encoded": "A boolean flag to indicate if the applicable request payload is Base64-encode"
            }

            https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
        
        Returns
        ------
        
        API Gateway Lambda Proxy Output Format: dict
            'statusCode' and 'body' are required

            {
                "isBase64Encoded": true | false,
                "statusCode": httpStatusCode,
                "headers": {"headerName": "headerValue", ...},
                "body": "..."
            }

            # api-gateway-simple-proxy-for-lambda-output-format
            https: // docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
        
    """

    message = get_message()

    return {
        "statusCode": 200,
        "body": json.dumps(message)
    }


def get_message():
    return {"hello": "world"}
