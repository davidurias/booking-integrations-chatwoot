import os
import json
from datetime import datetime
from aws_xray_sdk.core import patch_all
from sqlalchemy import desc
from shared_layer.base import Base
from shared_layer.common import Common
from shared_layer.model_integrations import BeweClient, BeweWork

if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None:
    patch_all()

def handler(event, context):
    common = Common()
    _, session = common.engine_create([Base])
    
    try:
        # Get chatwoot_contact_id from query parameters
        if not event.get('queryStringParameters') or not event['queryStringParameters'].get('contact_id'):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing contact_id parameter'
                })
            }
            
        chatwoot_contact_id = event['queryStringParameters']['contact_id']
        
        # Find the client by chatwoot_contact_id
        client = session.query(BeweClient).filter(
            BeweClient.chatwoot_contact_id == chatwoot_contact_id
        ).first()
        
        if not client:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Client not found'
                })
            }
        
        # Get the last 5 works for this client
        works = session.query(BeweWork).filter(
            BeweWork.bewe_client_id == client.id
        ).order_by(desc(BeweWork.work_time)).limit(5).all()
        
        # Format the response
        works_data = []
        for work in works:
            works_data.append({
                'id': work.id,
                'status': work.state,
                'work_time': work.work_time.isoformat() if work.work_time else None,
                'last_modification': work.last_modification
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'works': works_data,
                'meta': {
                    'count': len(works_data)
                }
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        } 