import requests
import json
import logging
import re

def setup_gemini(gemini_api, gemini_api_key):
    """
    Sets up the Gemini API URL.
    """
    return f"{gemini_api}={gemini_api_key}"

def ask_gemini(gemini_url, headers, data):
    """
    Sends a POST request to the specified URL.
    """
    return requests.post(gemini_url, headers=headers, json=data)

def replace_double_stars_in_response(response):
    """
    Replaces double stars in the response with a single star.
    """
    content_json = json.loads(response.content.decode())
    if 'candidates' in content_json and len(content_json['candidates']) > 0:
        candidate = content_json['candidates'][0]
        if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
            quote = candidate['content']['parts'][0]['text']
            logging.info(f"Quote recieved from GEMINI: {quote}")
            new_quote = quote.replace("**", "")
            return new_quote
        else:
            logging.error("Error: 'content' or 'parts' not found in the response")
            return None
    else:
        logging.error("Error: No 'candidates' found in the response")
        return None

def extract_quote_and_character(quote):
    """
    Extracts the quote and the character from the string.
    """
    # Split the quote using the pattern "::"
    parts = re.split(r"::", quote)

    # If there are two parts, assume the first part is the quote and the second part is the character
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    else:
        # If not split correctly, return the original quote and an empty character
        return quote, ""

