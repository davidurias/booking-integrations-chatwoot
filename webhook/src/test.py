import json
import pprint
import boto3
import os

from index import handler
from shared_layer.base import Base
from shared_layer.common import Common
from shared_layer.model_integrations import BeweClient, BeweWork

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
#print(sqs_message)

event = {}
event["Records"] = []
event["Records"].append({})

if sqs: 
    event["Records"][0]["messageId"] = sqs_message["Messages"][0]["MessageId"]
    event["Records"][0]["receiptHandle"] = sqs_message["Messages"][0]["ReceiptHandle"]
    event["Records"][0]["body"] = sqs_message["Messages"][0]["Body"]
else:
    event["Records"][0]["messageId"] = "xxxzzzxxx"
    event["Records"][0]["receiptHandle"] = "xxxxxxxx"
    
    ##New Work
    """ event["Records"][0]["body"] = json.dumps({
        "_id": "XXXXXXXXXXXXXXXXXXXXXXXX",
        "_idBHAccount": "644c0a5a109f8cf3d8b3130d",
        "eventName" : "newWork",
        "idClient": "XXXXXXXXXXXXXXXXXXXXXXXX",
        "state": "res",
        "day": "2025-03-01T00:00:00.000Z",
        "iniHour": "16:00",
        "dataClient": {
            "fullname": "David Urias",
            "phone": "+5216699946263",
        }
    }) """

    ##Update Work
    event["Records"][0]["body"] = json.dumps({
        "_id": "XXXXXXXXXXXXXXXXXXXXXXXX",
        "_idBHAccount": "644c0a5a109f8cf3d8b3130d",
        "eventName" : "updateWork",
        "idClient": "645d4a78db021aeb2a1b7f8e",
        "state": "confirmed",
        "newWork": {
            "day": "2025-03-01T00:00:00.000Z",
            "iniHour": "11:00",
        },
        "dataClient": {
            "fullname": "Generico V2",
            "phone": "+5216699946263",
        },
        "datemod":"2025-02-28T19:40:51.192Z"
    })
handler(event=event, context={})

if sqs:
    sqs_client.delete_message(
        QueueUrl=SQS_URL,
        ReceiptHandle=sqs_message["Messages"][0]["ReceiptHandle"]
    )
print("Message deleted.")

common = Common()
_, session = common.engine_create([
    Base
])

row = session.get(BeweWork, "XXXXXXXXXXXXXXXXXXXXXXXX")
print(row.__dict__)

""" session.delete(session.query(BeweWork).filter(
    BeweWork.id == "XXXXXXXXXXXXXXXXXXXXXXXX").first())
session.commit()
print("Record deleted.") """