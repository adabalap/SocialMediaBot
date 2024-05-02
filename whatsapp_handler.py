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

    payload = {'chatId': config["whatsapp_chat_id"], 'text': whatsapp_update, 'session': 'default'}
    whatsapp_api_headers = '{"Content-Type": "application/json"}'
    whatsapp_api_headers_dict = json.loads(whatsapp_api_headers)

    response = requests.post(
        config["whatsapp_api_url"],
        json=payload,
        headers=json.loads(whatsapp_api_headers),  # Load headers directly
        auth=(config["whatsapp_api_key"], '')
    )

    if response.status_code == 200 or response.status_code == 201:
        logging.info("WhatsApp message sent!")
        return True
    else:
        logging.error(f"Error while sending WhatsApp message: {response.status_code}")
        return False

