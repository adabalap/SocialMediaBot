import requests
import logging
import json

def setup_whatsapp(whatsapp_api_url, whatsapp_api_key):
    """
    Sets up the WhatsApp API URL and headers.
    """
    logging.debug("Entering setup_whatsapp function.")
    whatsapp_api_headers = '{"Content-Type": "application/json"}'
    whatsapp_api_headers_dict = json.loads(whatsapp_api_headers)
    logging.debug(f"WhatsApp API URL: {whatsapp_api_url}")
    logging.debug(f"WhatsApp API Headers: {whatsapp_api_headers_dict}")
    logging.debug("Exiting setup_whatsapp function.")
    return whatsapp_api_url, whatsapp_api_headers_dict, whatsapp_api_key

def send_to_whatsapp(config, quote, character, quote_prefix, quote_suffix):
    """
    Sends the quote to WhatsApp.
    """
    logging.debug("Entering send_to_whatsapp function.")
    logging.debug("Preparing the quote for WhatsApp.")
    quote = f"*{quote}*"  # Add asterisks to make the quote bold in WhatsApp
    if character:
        whatsapp_update = f"{quote_prefix}  {quote} \n\n-{character}"
    else:
        whatsapp_update = f"{quote_prefix}  {quote}"

    logging.debug(f"Formatted WhatsApp Update: {whatsapp_update}")

    payload = {'message': whatsapp_update}
    headers = {
        'Content-Type': 'application/json'
    }

    if config.get("whatsapp_status") == "yes":
        url = config["whatsapp_status_api_url"]  # Use the status API URL from config
        logging.debug("Configured to send to WhatsApp status.")
    else:
        payload.update({'chatId': config["whatsapp_chat_id"], 'session': 'default'})
        url = config["whatsapp_api_url"]
        logging.debug("Configured to send to WhatsApp chat.")

    logging.debug(f"Payload to be sent: {payload}")
    logging.debug(f"URL to be used: {url}")
    logging.debug(f"Headers to be used: {headers}")

    logging.debug("Sending request to WhatsApp API.")
    response = requests.post(url, json=payload, headers=headers, auth=(config["whatsapp_api_key"], ''))

    logging.debug(f"Received response with status code: {response.status_code}")
    logging.debug(f"Response content: {response.content}")

    if response.status_code in [200, 201]:
        logging.info("WhatsApp message sent successfully!")
        logging.debug("Exiting send_to_whatsapp function with success.")
        return True
    else:
        logging.error(f"Error while sending WhatsApp message: {response.status_code}")
        logging.debug("Exiting send_to_whatsapp function with failure.")
        return False
