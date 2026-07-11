import os
import json
import boto3
from datetime import datetime
from datetime import timezone

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def lambda_handler(event, context):
    try:
        # Extract the raw request body from API Gateway
        raw_body = event.get('body', '{}')
        body_json = json.loads(raw_body)
        
        # Determine a filename based on payload data or timestamp
        event_id = body_json.get('event_id', datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f'))
        event_type = body_json.get('event', 'unknown_event')
        s3_key = f"{event_type}/{event_id}.json"
        
        # Save JSON payload directly to the Amazon S3 Bucket
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=raw_body,
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Webhook saved to S3 successfully'})
        }
        
    except Exception as e:
        print(f"Error handling webhook: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server processing error'})
        }
