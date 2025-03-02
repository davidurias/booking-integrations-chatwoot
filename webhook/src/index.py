from datetime import datetime, timezone
import os
import json

import pytz
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import requests
from shared_layer.base import Base
from shared_layer.common import Common
from shared_layer.model_integrations import MessageConfirmation

if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None:
    patch_all()

session = None
common = Common()

def bewe_api_work_state_update(bewe_work, state):
    url = f"https://api.bewe.io/v1/centers/booking/{bewe_work.id}"
    headers = {
        'content-type': 'application/json',
        'authorization': 'Bearer ' + bewe_work.bewe_account.bewe_apikey
    } 

    response = requests.put(url, headers=headers, json={"state": state})
    print(response.text)
    if response.status_code == 200:
        return True
    else:
        return None

def msg_confirm(msg):
    reply_msg_id = msg["content_attributes"]["in_reply_to"]
    print(reply_msg_id)

    msg_confirmation = session.query(MessageConfirmation).filter(
        MessageConfirmation.chatwoot_message_id == reply_msg_id
    ).first()
    if not msg_confirmation:
       raise Exception("Something went wrong!")

    work_sate = msg_confirmation.bewe_work.state

    if work_sate == "res":

        content = "Hola, gracias por tu confirmación, te estaremos esperando para tu cita. ¡Gracias!."
        template_params = {
            "name": "cita_confirmacion_confirmar",
            "category": "utility",
            "language": "es_mx",
        }

        common.message_send(msg_confirmation, content, template_params, session, False)

        confirmations = session.query(MessageConfirmation).filter(
            MessageConfirmation.chatwoot_message_id == msg_confirmation.chatwoot_message_id
        ).all()

        for confirmation in confirmations:
            print("updating work state")
            confirmation.bewe_work.state = "confirmed"
            session.commit()
            bewe_api_work_state_update(confirmation.bewe_work, "confirmed")

    else:
        content = "Hola, tu cita ya ha sido cancelada con anterioridad, no es posible confirmarla en este momento"
        template_params = {
            "name": "reply_confirmar_cancelada",
            "category": "utility",
            "language": "es_mx",
            "processed_params" : {
                1: msg_confirmation.bewe_client.bewe_account.name,
                2: msg_confirmation.bewe_client.bewe_account.phone_number
            }
        }

        common.message_send(msg_confirmation, content, template_params, session, False)

def msg_cancel(msg):
    reply_msg_id = msg["content_attributes"]["in_reply_to"]
    print(reply_msg_id)
    msg_confirmation = session.query(MessageConfirmation).filter(
        MessageConfirmation.chatwoot_message_id == reply_msg_id
    ).first()
    if not msg_confirmation:
       raise Exception("Something went wrong!")

    work_sate = msg_confirmation.bewe_work.state

    if work_sate == "res" or work_sate == "confirmed":
        content = "Hola, su cita ha sido cancelada, lamentamos que no puedas asistir, ¡Saludos!"
        template_params = {
            "name": 'reply_cancel',
            "category": 'utility',
            "language": 'es_mx',
        }
        common.message_send(msg_confirmation, content, template_params, session, False)

        work_state = "res_missing"

        hours_diff = common.get_hours_between_dates(datetime.now(pytz.utc).isoformat(), msg_confirmation.bewe_work.work_time.isoformat())

        print(hours_diff)

        if msg_confirmation.bewe_client.bewe_account.reminder_time + 1 < hours_diff: 
            work_state = "res_client_rejected"

        confirmations = session.query(MessageConfirmation).filter(
            MessageConfirmation.chatwoot_message_id == msg_confirmation.chatwoot_message_id
        ).all()

        print(work_state)

        for confirmation in confirmations:
            confirmation.bewe_work.state = work_state
            session.commit()
            bewe_api_work_state_update(confirmation.bewe_work, work_state)
        
    else:
        content = "Hola, tu cita ya ha sido cancelada con anterioridad, no es posible cancelarla en este momento"
        template_params = {
            "name": "reply_cancelar_cancelada",
            "category": "utility",
            "language": "es_mx",
            "processed_params" : {
                1: msg_confirmation.bewe_client.bewe_account.name,
                2: msg_confirmation.bewe_client.bewe_account.phone_number
            }
        }
        common.message_send(msg_confirmation, content, template_params, session, False)


def handler(event, context):

    global session

    _, session = common.engine_create([
        Base
    ])

    for record in event['Records']:
        print("Initiating record processing")
        msg = json.loads(record["body"])
        
        msg_type = msg["message_type"]

        #print(msg)

        if msg_type == "incoming":
            msg_content = msg["content"]         
            match msg_content:
                case "CONFIRMAR":
                    print("confirmar")
                    msg_confirm(msg)
                case "CANCELAR":
                    print("cancelar")
                    msg_cancel(msg)

