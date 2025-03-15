import boto3
import os

from index import handler

sqs = False

ENV = os.getenv('ENV', default="local")
if ENV == "local":
    os.environ["DB_HOST"] = 'db.cdwkkckoowxq.us-east-1.rds.amazonaws.com'
    os.environ["DB_USER"] = 'integrations'
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_NAME"] = 'integrations'

SQS_URL = 'https://sqs.us-east-1.amazonaws.com/992382547995/integrations-bewe-clientNew'
SQS_DLQ_URL = 'https://sqs.us-east-1.amazonaws.com/992382547995/integrations-bewe-clientNew-dlq'

if sqs:
    sqs_client = boto3.client('sqs')
    sqs_message = sqs_client.receive_message(
        QueueUrl=SQS_URL,
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All'],
        VisibilityTimeout=5,
        WaitTimeSeconds=0
    )
    if not 'Messages' in sqs_message:
        SQS_URL = SQS_DLQ_URL
        sqs_message = sqs_client.receive_message(
            QueueUrl=SQS_DLQ_URL,
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=5,
            WaitTimeSeconds=0
        )
# print(sqs_message)

event = {}
handler(event=event, context={})
