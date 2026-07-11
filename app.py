import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigwv2,              # Stable module
    aws_apigatewayv2_integrations as integrations # Stable module
)
from constructs import Construct

class CalendlyWebhookStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create secure S3 Bucket to hold the raw webhook bodies
        webhook_raw_bucket = s3.Bucket(
            self, "CalendlyRawWebhookBucket",
            bucket_name="calendly-raw-webhook-data",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN # Keeps data if stack is deleted
        )

        # 2. Create secure S3 Bucket to hold the processed webhook data
        webhook_processed_bucket = s3.Bucket(
            self, "CalendlyProcessedWebhookBucket",
            bucket_name="calendly-processed-webhook-data",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN # Keeps data if stack is deleted
        )

        # 3. Create the Lambda Function
        webhook_handler = _lambda.Function(
            self, "CalendlyWebhookHandler",
            function_name="calendly-webhook-handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_ingestion"),
            environment={
                "BUCKET_NAME": webhook_raw_bucket.bucket_name
            }
        )

        # 4. Grant Lambda explicit IAM permission to write to S3
        webhook_raw_bucket.grant_write(webhook_handler)

        # 5. Create the API Gateway HTTP API
        http_api = apigwv2.HttpApi(
            self, "CalendlyWebhookApi",
            api_name="calendly-webhook-api"
        )

        # 6. Connect API Gateway to Lambda
        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            handler=webhook_handler
        )

        # 7. Add POST /webhook route
        http_api.add_routes(
            path="/webhook",
            methods=[apigwv2.HttpMethod.POST],
            integration=lambda_integration
        )

        # Output the public URL to CLI/Logs upon successful deployment
        cdk.CfnOutput(
            self, "WebhookSubscriptionUrl",
            value=f"{http_api.url}webhook",
            description="The URL to provide to Calendly for the webhook subscription"
        )

app = cdk.App()
CalendlyWebhookStack(app, "CalendlyWebhookStack")
app.synth()
