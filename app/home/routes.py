import logging
import json
import requests
import os
import xml.etree.ElementTree as ET


from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)


home = Blueprint('home', __name__)
home.json_encoder = CustomJSONEncoder

limiter = Limiter(app, key_func=get_remote_address)
discord_webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
teams_webhook_url = os.environ.get('TEAMS_WEBHOOK_URL')


@home.route('/home')
@home.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def homepage():
    return render_template('home.html', title='NC_XML_Receiver')


@home.route('/receiver_discord', methods=['POST'])
@limiter.limit("5 per minute")
def soap_receiver_discord():
    try:
        xml_data = request.data.decode('utf-8')
        normalized_data = normalize_xml(xml_data)

        if 'error' in normalized_data:
            logging.error(f"Error normalizing XML data: {normalized_data['error']}")
            return jsonify({'success': False, 'message': 'Error processing request'}), 500  # Internal Server Error

        send_to_discord_webhook(normalized_data)

        logging.info("XML data received and processed successfully for Discord")
        return jsonify({'success': True, 'message': 'XML data received and processed successfully for Discord'})

    except Exception as e:
        logging.error(f"Error processing SOAP request for Discord: {str(e)}")
        return jsonify({'success': False, 'message': 'Error processing request'}), 500  # Internal Server Error
    
    
def normalize_xml(xml_data):
    try:
        root = ET.fromstring(xml_data)

        qualitative_new_state = root.findtext('QualitativeNewState')

        if qualitative_new_state in ['Failed', 'Warning']:
            notification_type = 'Service Failure'
            notification_trigger_id = root.findtext('ActiveNotificationTriggerID')
            customer_name = root.findtext('CustomerName')
            device_name = root.findtext('DeviceName')
            device_uri = root.findtext('DeviceURI')
            affected_service = root.findtext('AffectedService')
            time_of_state_change_str = root.findtext('TimeOfStateChange')
            probe_uri = root.findtext('ProbeURI')
            quantitative_new_state = root.findtext('QuantitativeNewState')
            qualitative_new_state = root.findtext('QualitativeNewState')
            qualitative_old_state = root.findtext('QualitativeOldState')

            time_of_state_change = datetime.strptime(time_of_state_change_str, '%Y-%m-%d %H:%M:%S')

            normalized_data = {
                'notification_type': notification_type,
                'notification_trigger_id': notification_trigger_id,
                'customer_name': customer_name,
                'device_name': device_name,
                'device_uri': device_uri,
                'affected_service': affected_service,
                'qualitative_new_state': qualitative_new_state,
                'qualitative_old_state': qualitative_old_state,
                'time_of_state_change': time_of_state_change,
                'probe_uri': probe_uri,
                'quantitative_new_state': quantitative_new_state

            }

        elif qualitative_new_state == 'Normal':
            notification_type = 'RTN'
            customer_name = root.findtext('CustomerName')
            device_name = root.findtext('DeviceName')
            device_uri = root.findtext('DeviceURI')
            affected_service = root.findtext('AffectedService')
            qualitative_old_state = root.findtext('QualitativeOldState')
            qualitative_new_state = root.findtext('QualitativeNewState')
            time_of_state_change_str = root.findtext('TimeOfStateChange')
            probe_uri = root.findtext('ProbeURI')
            remote_control_link = root.findtext('RemoteControlLink')
            active_profile = root.findtext('ActiveProfile')
            quantitative_new_state = root.findtext('QuantitativeNewState')

            time_of_state_change = datetime.strptime(time_of_state_change_str, '%Y-%m-%d %H:%M:%S')

            normalized_data = {
                'notification_type': notification_type,
                'customer_name': customer_name,
                'device_name': device_name,
                'device_uri': device_uri,
                'affected_service': affected_service,
                'qualitative_new_state': qualitative_new_state,
                'qualitative_old_state': qualitative_old_state,
                'time_of_state_change': time_of_state_change,
                'probe_uri': probe_uri,
                'remote_control_link': remote_control_link,
                'active_profile': active_profile,
                'quantitative_new_state': quantitative_new_state
            }

        else:
            normalized_data = {'error': 'Unknown notification type'}

        return normalized_data

    except Exception as e:
        logging.error(f"Error normalizing XML data: {str(e)}")
        return {}


def send_to_discord_webhook(data):
    webhook = DiscordWebhook(url=discord_webhook_url, username="NC Receiver")

    embed = DiscordEmbed(title='SOAP Notification', color=2368548)

    time_of_state_change_str = data.get('time_of_state_change', '')
    if isinstance(time_of_state_change_str, datetime):
        time_of_state_change_str = time_of_state_change_str.strftime('%Y-%m-%d %H:%M:%S')


    if data['notification_type'] == 'Service Failure':
        embed.set_footer(text="https://nc.syschimp.com")
        embed.set_timestamp()
        embed.add_embed_field(name='Notification Type', value=data.get('notification_type', ''))
        embed.add_embed_field(name='Notification Trigger ID', value=data.get('notification_trigger_id', ''))
        embed.add_embed_field(name='Customer Name', value=data.get('customer_name', ''))
        embed.add_embed_field(name='Device Name', value=data.get('device_name', ''))
        embed.add_embed_field(name='Device URI', value=data.get('device_uri', ''))
        embed.add_embed_field(name='Affected Service', value=data.get('affected_service', ''))
        embed.add_embed_field(name='Qualitative New State', value=data.get('qualitative_new_state', ''))
        embed.add_embed_field(name='Qualitative Old State', value=data.get('qualitative_old_state', ''))
        embed.add_embed_field(name='Time of State Change', value=time_of_state_change_str)
        embed.add_embed_field(name='Probe URI', value=data.get('probe_uri', ''))
        embed.add_embed_field(name='Quantitative New State', value=data.get('quantitative_new_state', ''))


    elif data['notification_type'] == 'RTN':
        embed.set_footer(text="https://nc.syschimp.com")
        embed.set_timestamp()
        embed.add_embed_field(name='Notification Type', value=data.get('notification_type', ''))
        embed.add_embed_field(name='Customer Name', value=data.get('customer_name', ''))
        embed.add_embed_field(name='Device Name', value=data.get('device_name', ''))
        embed.add_embed_field(name='Device URI', value=data.get('device_uri', ''))
        embed.add_embed_field(name='Affected Service', value=data.get('affected_service', ''))
        embed.add_embed_field(name='Qualitative New State', value=data.get('qualitative_new_state', ''))
        embed.add_embed_field(name='Qualitative Old State', value=data.get('qualitative_old_state', ''))
        embed.add_embed_field(name='Time of State Change', value=time_of_state_change_str)
        embed.add_embed_field(name='Probe URI', value=data.get('probe_uri', ''))
        embed.add_embed_field(name='Remote Control Link', value=data.get('remote_control_link', ''))
        embed.add_embed_field(name='Active Profile', value=data.get('active_profile', ''))
        embed.add_embed_field(name='Quantitative New State', value=data.get('quantitative_new_state', ''))

    webhook.add_embed(embed)

    response = webhook.execute()
    logging.info("Discord message sent")
    print(response)

    return response


@home.route('/receiver_teams', methods=['POST'])
@limiter.limit("5 per minute")
def soap_receiver_teams():
    try:
        xml_data = request.data.decode('utf-8')
        normalized_data = normalize_xml(xml_data)

        send_to_teams_webhook(normalized_data, teams_webhook_url)

        logging.info("XML data received and processed successfully for Teams")
        return jsonify({'success': True, 'message': 'XML data received and processed successfully for Teams'})

    except Exception as e:
        logging.error(f"Error processing SOAP request for Teams: {str(e)}")
        return jsonify({'success': False, 'message': 'Error processing SOAP request for Teams'})


def send_to_teams_webhook(data):
    time_of_state_change_str = data.get('time_of_state_change', '').strftime('%Y-%m-%d %H:%M:%S')

    if data['notification_type'] == 'Service Failure':
        payload = {
            "title": "SOAP Notification - Service Failure",
            "text": f"Notification Type: {data.get('notification_type', '')}\n"
                    f"Notification Trigger ID: {data.get('notification_trigger_id', '')}\n"
                    f"Customer Name: {data.get('customer_name', '')}\n"
                    f"Device Name: {data.get('device_name', '')}\n"
                    f"Device URI: {data.get('device_uri', '')}\n"
                    f"Affected Service: {data.get('affected_service', '')}\n"
                    f"Qualitative New State: {data.get('qualitative_new_state', '')}\n"
                    f"Qualitative Old State: {data.get('qualitative_old_state', '')}\n"
                    f"Time of State Change: {time_of_state_change_str}\n"
                    f"Probe URI: {data.get('probe_uri', '')}\n"
                    f"Quantitative New State: {data.get('quantitative_new_state', '')}"
        }
    elif data['notification_type'] == 'RTN':
        payload = {
            "title": "SOAP Notification - RTN",
            "text": f"Notification Type: {data.get('notification_type', '')}\n"
                    f"Customer Name: {data.get('customer_name', '')}\n"
                    f"Device Name: {data.get('device_name', '')}\n"
                    f"Device URI: {data.get('device_uri', '')}\n"
                    f"Affected Service: {data.get('affected_service', '')}\n"
                    f"Qualitative New State: {data.get('qualitative_new_state', '')}\n"
                    f"Qualitative Old State: {data.get('qualitative_old_state', '')}\n"
                    f"Time of State Change: {time_of_state_change_str}\n"
                    f"Probe URI: {data.get('probe_uri', '')}\n"
                    f"Remote Control Link: {data.get('remote_control_link', '')}\n"
                    f"Active Profile: {data.get('active_profile', '')}\n"
                    f"Quantitative New State: {data.get('quantitative_new_state', '')}"
        }
    else:
        payload = {"title": "Unknown Notification Type", "text": "Unhandled notification type"}

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(teams_webhook_url, data=json.dumps(payload), headers=headers)

        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        logging.info("Microsoft Teams message sent")
        print(response.text)
        return response.json()  # Return the response as JSON if applicable
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message to Microsoft Teams: {str(e)}")
        return None
