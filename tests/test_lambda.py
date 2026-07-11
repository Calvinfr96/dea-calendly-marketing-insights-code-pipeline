import os
import json
from unittest.mock import patch, MagicMock

# Set environmental variables required by the Lambda handler before import
os.environ['BUCKET_NAME'] = 'test-calendly-bucket'
from lambda_ingestion.handler import lambda_handler

@patch('lambda_ingestion.handler.s3_client')
def test_lambda_handler_success(mock_s3):
    # Mock data modeling an API Gateway event payload
    fake_event = {
        "body": json.dumps({
            "event": "invitee.created",
            "event_id": "test_12345",
            "payload": {"email": "test@example.com"}
        })
    }
    
    # Execute the handler function
    response = lambda_handler(fake_event, None)
    
    # Assertions
    assert response['statusCode'] == 200
    assert 'Webhook saved to S3 successfully' in response['body']
    
    # Verify s3 client was called with exact correct arguments
    mock_s3.put_object.assert_called_once_with(
        Bucket='test-calendly-bucket',
        Key='invitee.created/test_12345.json',
        Body=fake_event['body'],
        ContentType='application/json'
    )

def test_lambda_handler_malformed_json():
    # Execute handler with bad json data to verify failure resilience
    fake_event = {"body": "invalid-json-string"}
    
    response = lambda_handler(fake_event, None)
    assert response['statusCode'] == 500
