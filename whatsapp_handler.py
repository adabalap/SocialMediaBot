import requests
import logging
import json

def setup_whatsapp(whatsapp_api_url, whatsapp_api_key):
    """
    Sets up the WhatsApp API URL and headers.
    """
    whatsapp_api_headers = '{"Content-Type": "application/json"}'
    whatsapp_api_headers_dict = json.loads(whatsapp_api_headers)
    return whatsapp_api_url, whatsapp_api_headers_dict, whatsapp_api_key

def send_to_whatsapp(config, quote, character, quote_prefix, quote_suffix):
    """
    Sends the quote to WhatsApp.
    """
    quote = f"*{quote}*"  # Add asterisks to make the quote bold in WhatsApp
    if character:
        whatsapp_update = f"{quote_prefix}  {quote} \n\n-{character}"
    else:
        whatsapp_update = f"{quote_prefix}  {quote}"

    payload = {'message': whatsapp_update}
    headers = {
        'Content-Type': 'application/json'
    }

    if config.get("whatsapp_status") == "yes":
        url = config["whatsapp_status_api_url"]  # Use the status API URL from config
    else:
        payload.update({'chatId': config["whatsapp_chat_id"], 'session': 'default'})
        url = config["whatsapp_api_url"]

    response = requests.post(url, json=payload, headers=headers, auth=(config["whatsapp_api_key"], ''))

    if response.status_code in [200, 201]:
        logging.info("WhatsApp message sent!")
        return True
    else:
        logging.error(f"Error while sending WhatsApp message: {response.status_code}")
        return False
