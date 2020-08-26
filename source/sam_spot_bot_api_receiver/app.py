import json
import uuid
import boto3

# Global variables are reused across execution contexts (if available)
session = boto3.Session()


def lambda_handler(event, context):
    """
        AWS Lambda handler

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

    global bulk_size, number_of_bots, s3_bucket, s3_path, output_s3_bucket
    print("Received event: " + json.dumps(event, indent=2))
    httpMethod = ''
    if event["httpMethod"] == "POST":
        httpMethod = 'POST'
    elif event["httpMethod"] == "DELETE":
        httpMethod = 'DELETE'
    else:
        respond(res={"err": "Method is not allowed."})

    # Read the request parameter.
    request_body = json.loads(event["body"])
    bot_name = request_body["bot_name"]

    if httpMethod == "POST":
        bulk_size = request_body["bulk_size"]
        number_of_bots = request_body["number_of_bots"]
        s3_bucket = request_body["s3_bucket"]
        s3_path = request_body["s3_path"]
        output_s3_bucket = request_body['output_s3_bucket']
        output_s3_prefix = request_body['output_s3_prefix']
        if int(number_of_bots) < 1:
            return respond(ValueError('number of bot need to great then 0'))
    elif httpMethod == "DELETE":
        bulk_size = ""
        number_of_bots = ""
        s3_bucket = ""
        s3_path = ""
        output_s3_bucket = ""
        output_s3_prefix = ""

    job_id = str(uuid.uuid4())
    client = boto3.client('lambda')

    args = {
            "httpMethod": httpMethod,
            "bot_name": bot_name,
            "bulk_size": bulk_size,
            "number_of_bots": number_of_bots,
            "s3_bucket": s3_bucket,
            "s3_path": s3_path,
            "output_s3_bucket": output_s3_bucket,
            "output_s3_prefix": output_s3_prefix,
            "job_id": job_id
            }
    response = client.invoke_async(
        FunctionName='sam_spot_bot_create_job',
        InvokeArgs=json.dumps(args)
    )

    print("<<<< Exist and calling the real worker Lambda function- spot_bot_create_job > " + str(args))
    body = {"job_id": job_id}
    return respond(None, body)  # respond 201 created.


def respond(err: Exception, res=None):
    return {
        'statusCode': 400 if err else 201,
        'body': err["msg"] if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
