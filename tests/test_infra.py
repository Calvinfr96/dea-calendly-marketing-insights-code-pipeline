import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
from app import CalendlyWebhookStack

def test_infrastructure_stack():
    app = cdk.App()
    stack = CalendlyWebhookStack(app, "TestStack")
    template = Template.from_stack(stack)

    # 1. Assert an S3 Bucket is created with public access explicitly blocked
    template.has_resource_properties("AWS::S3::Bucket", {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "BlockPublicPolicy": True,
            "IgnorePublicAcls": True,
            "RestrictPublicBuckets": True
        }
    })

    # 2. Assert a Python 3.12 Lambda function is generated
    template.has_resource_properties("AWS::Lambda::Function", {
        "Runtime": "python3.12",
        "Handler": "handler.lambda_handler"
    })

    # 3. Assert an API Gateway HTTP route exists for POST /webhook
    template.has_resource_properties("AWS::ApiGatewayV2::Route", {
        "RouteKey": "POST /webhook"
    })
