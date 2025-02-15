import requests
import logging
import json

def setup_whatsapp(whatsapp_api_url, whatsapp_api_key):
    """
    Sets up the WhatsApp API URL and headers.
    """
    logging.info("Entering setup_whatsapp function.")
    whatsapp_api_headers = '{"Content-Type": "application/json"}'
    whatsapp_api_headers_dict = json.loads(whatsapp_api_headers)
    logging.info(f"WhatsApp API URL: {whatsapp_api_url}")
    logging.info(f"WhatsApp API Headers: {whatsapp_api_headers_dict}")
    logging.info("Exiting setup_whatsapp function.")
    return whatsapp_api_url, whatsapp_api_headers_dict, whatsapp_api_key

def send_to_whatsapp(config, quote, character, quote_prefix, quote_suffix):
    """
    Sends the quote to WhatsApp.
    """
    logging.info("Entering send_to_whatsapp function.")
    logging.info("Preparing the quote for WhatsApp.")
    quote = f"*{quote}*"  # Add asterisks to make the quote bold in WhatsApp
    if character:
        whatsapp_update = f"{quote_prefix}  {quote} \n\n-{character}"
    else:
        whatsapp_update = f"{quote_prefix}  {quote}"

    logging.info(f"Formatted WhatsApp Update: {whatsapp_update}")

    payload = {
        'contacts': None,
        'text': whatsapp_update,
        'backgroundColor': '#38b42f',  # You can customize this color
        'font': 0  # You can customize the font
    }
    headers = {
        'Content-Type': 'application/json',
        'accept': '*/*'
    }

    if config.get("whatsapp_status") == "yes":
        url = config["whatsapp_status_api_url"]  # Use the status API URL from config
        logging.info("Configured to send to WhatsApp status.")
    else:
        payload.update({'chatId': config["whatsapp_chat_id"], 'session': 'default'})
        url = config["whatsapp_api_url"]
        logging.info("Configured to send to WhatsApp chat.")

    logging.info(f"Payload to be sent: {payload}")
    logging.info(f"URL to be used: {url}")
    logging.info(f"Headers to be used: {headers}")

    logging.info("Sending request to WhatsApp API.")
    response = requests.post(url, json=payload, headers=headers, auth=(config["whatsapp_api_key"], ''))

    logging.info(f"Received response with status code: {response.status_code}")
    logging.info(f"Response content: {response.content}")

    if response.status_code in [200, 201]:
        logging.info("WhatsApp message sent successfully!")
        logging.info("Exiting send_to_whatsapp function with success.")
        return True
    else:
        logging.error(f"Error while sending WhatsApp message: {response.status_code}")
        logging.info("Exiting send_to_whatsapp function with failure.")
        return False
