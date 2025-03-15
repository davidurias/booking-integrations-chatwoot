from datetime import datetime
import os
import pytz
from sqlalchemy import update
from aws_xray_sdk.core import patch_all
from shared_layer.base import Base
from shared_layer.common import Common
from shared_layer.model_integrations import MessageConfirmation, MessageReminder

if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None:
    patch_all()

session = None
common = Common()

start_of_work, end_of_work = common.get_start_end_work(
    datetime.now(pytz.utc), 0)


def process_confirmations(confirmation):

    start_of_day, end_of_day = common.get_start_end_day(common.convert_date_to_timezone(
        datetime.now(pytz.utc), confirmation.bewe_client.bewe_account.timezone))

    work_time = common.convert_hour_to_timezone(
        confirmation.bewe_work.work_time, confirmation.bewe_work.bewe_account.timezone)

    content = f"Hola {confirmation.bewe_client.name} ,para recordarte que tienes una cita con nosotros el día de mañana a las {work_time}."
    template_params = {
        "name": "cita_confirmacion",
        "category": "utility",
        "language": "es_mx",
        "processed_params": {
            1: confirmation.bewe_client.name,
            2: work_time
        }
    }

    response = common.message_send(
        confirmation, content, template_params, session)

    # print(response)

    print(start_of_day, end_of_day)

    stmt = (
        update(MessageConfirmation)
        .where(
            MessageConfirmation.bewe_client_id == confirmation.bewe_client_id,
            MessageConfirmation.time.between(start_of_day, end_of_day)
        )
        .values(chatwoot_message_id=confirmation.chatwoot_message_id)
    )

    # Execute the update statement
    session.execute(stmt)
    session.commit()


def process_reminders(reminder):
    start_of_day, end_of_day = common.get_start_end_day(common.convert_date_to_timezone(
        datetime.now(pytz.utc), reminder.bewe_client.bewe_account.timezone))

    work_time = common.convert_hour_to_timezone(
        reminder.bewe_work.work_time, reminder.bewe_work.bewe_account.timezone)

    content = f"Hola {reminder.bewe_client.name}, para recordarte que tienes una cita con nosotros el día de hoy a las {work_time}, recuerda salir con anticipación, ya que cuentas con 10 minutos de tolerancia."
    template_params = {
        "name": "cita_recordatorio",
        "category": "utility",
        "language": "es_mx",
        "processed_params": {
            1: reminder.bewe_client.name,
            2: work_time
        }
    }

    response = common.message_send(reminder, content, template_params, session)

    # print(response)

    print(start_of_day, end_of_day)

    stmt = (
        update(MessageReminder)
        .where(
            MessageReminder.bewe_client_id == reminder.bewe_client_id,
            MessageReminder.time.between(start_of_day, end_of_day)
        )
        .values(chatwoot_message_id=reminder.chatwoot_message_id)
    )

    # Execute the update statement
    session.execute(stmt)
    session.commit()


def handler(event, context):

    global session

    _, session = common.engine_create([
        Base
    ])

    print(start_of_work, end_of_work)

    confirmations = session.query(MessageConfirmation).filter(
        MessageConfirmation.time.between(start_of_work, end_of_work),
        MessageConfirmation.chatwoot_message_id == None
    ).all()

    unique_confirmations = {}

    for confirmation in confirmations:
        # Assuming `client` is the relationship attribute
        bewe_client = confirmation.bewe_client
        client_id = bewe_client.id

        if client_id not in unique_confirmations or unique_confirmations[client_id].time > confirmation.time:
            # Store the entire confirmation object
            unique_confirmations[client_id] = confirmation

    for confirmation in unique_confirmations.values():
        if confirmation.bewe_work.bewe_client.phone_number is not None or confirmation.bewe_work.bewe_client.phone_number != "":
            process_confirmations(confirmation)

    remminders = session.query(MessageReminder).filter(
        MessageReminder.time.between(start_of_work, end_of_work),
        MessageReminder.chatwoot_message_id is None
    ).all()

    print(remminders)

    unique_reminders = {}

    for reminder in remminders:
        bewe_client = reminder.bewe_client
        client_id = bewe_client.id

        if client_id not in unique_reminders or unique_reminders[client_id].time > reminder.time:
            unique_reminders[client_id] = reminder

    for reminder in unique_reminders.values():
        if reminder.bewe_work.bewe_client.phone_number is not None or reminder.bewe_work.bewe_client.phone_number != "":
            process_reminders(reminder)
