import tweepy
import xmlrpc.client
import requests
import json
import os
import sys
import logging
import re
import sqlite3
from rapidfuzz import fuzz, process
from datetime import datetime
import time

class SocialMediaBot:
    def __init__(self):
        self.config = None
        self.auth = None
        self.api = None
        self.gemini_url = None
        self.conn = None
        self.cursor = None

    def setup_logging(self):
        """
        Sets up the logging configuration.
        """
        level = logging.INFO if self.config["logging_level"] == "INFO" else logging.DEBUG
        logging.basicConfig(
            filename=self.config["log_file"],
            level=level,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logging.info("Logging setup complete.")

    def load_config(self, config_file):
        """
        Loads the configuration file.
        """
        with open(config_file) as f:
            config = json.load(f)
        return config

    def setup_db(self):
        """
        Sets up the SQLite database.
        """
        self.conn = sqlite3.connect(self.config["db_file"])
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Quotes (
                id INTEGER PRIMARY KEY,
                character TEXT,
                quote TEXT UNIQUE,
                date TEXT,
                sent_to_twitter TEXT,
                sent_to_wordpress TEXT,
                sent_to_whatsapp TEXT
            )
        ''')
        self.conn.commit()

    def extract_quote_and_character(self, quote):
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

    def ask_gemini(self, url, headers, data):
        """
        Sends a POST request to the specified URL.
        """
        return requests.post(url, headers=headers, json=data)

    def replace_double_stars_in_response(self, response):
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

    def create_wp_post(self, quote, character, quote_prefix, quote_suffix):
        """
        Creates a new WordPress post with the successfully posted Twitter message.
        """
        if character:
            wp_update = f"{quote_prefix} {quote} - {character}"
        else:
            wp_update = f"{quote_prefix} {quote}"
        try:
            wp_url = self.config["wp_url"]
            wp_username = self.config["wp_username"]
            wp_password = self.config["wp_password"]
            wp_category = self.config["wp_category"]

            client = xmlrpc.client.ServerProxy(wp_url)

            post = {
                "post_type": "post",
                "post_status": "publish",
                "post_title": wp_update[:40] + "...",  # Use the first 40 characters of the update as the post title
                "post_content": wp_update,
                "terms_names": {
                    "category": [wp_category]  # The category of the post
                }
            }

            post_id = client.wp.newPost("", wp_username, wp_password, post)

            logging.info(f"WordPress post created with ID: {post_id}!")
            return True
        except Exception as e:
            logging.error(f"Error while creating WordPress post: {str(e)}")
            return False

    def tweet_quote(self, quote, character, quote_prefix, quote_suffix):
        """
        Tweets the quote with the specified prefix and suffix.
        """
        if character:
            tweet = f"{quote_prefix} {quote} - {character} {quote_suffix}"
        else:
            tweet = f"{quote_prefix} {quote} {quote_suffix}"

        if len(tweet) > 280:
            logging.info(tweet)
            logging.error("The combined length of the quote, prefix and suffix exceeds the Twitter character limit.")
            return False

        try:
            self.api.update_status(tweet)
            logging.info("Tweet sent!")
            return True
        except Exception as e:
            logging.error(f"Error while tweeting: {str(e)}")
            return False

    def send_to_whatsapp(self, quote, character, quote_prefix, quote_suffix):
        """
        Sends the quote to WhatsApp.
        """
        quote = f"*{quote}*"  # Add asterisks to make the quote bold in WhatsApp
        if character:
            whatsapp_update = f"{quote_prefix}  {quote} \n\n-{character}"
        else:
            whatsapp_update = f"{quote_prefix}  {quote}"

        payload = {'chatId': self.config["whatsapp_chat_id"], 'text': whatsapp_update, 'session': 'default'}
        whatsapp_api_headers = '{"Content-Type": "application/json"}'
        whatsapp_api_headers_dict = json.loads(whatsapp_api_headers)

        response = requests.post(
            self.config["whatsapp_api_url"],
            json=payload,
            headers=json.loads(whatsapp_api_headers),  # Load headers directly
            auth=(self.config["whatsapp_api_key"], '')
        )

        if response.status_code == 200 or response.status_code == 201:
            logging.info("WhatsApp message sent!")
            return True
        else:
            logging.error(f"Error while sending WhatsApp message: {response.status_code}")
            return False

    def run(self, config_file):
        """
        The main function of the script.
        """
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.setup_db()
        self.auth = tweepy.OAuthHandler(self.config["twitter_consumer_key"], self.config["twitter_consumer_secret"])
        self.auth.set_access_token(self.config["twitter_access_token"], self.config["twitter_access_token_secret"])
        self.api = tweepy.API(self.auth)
        self.gemini_url = f"{self.config['gemini_api']}={self.config['gemini_api_key']}"

        duplicate_quote_recieved = ""

        for i in range(self.config["max_gemini_attempts"]):
            if duplicate_quote_recieved:
                gemini_prompt = f"{self.config['gemini_prompt']} {duplicate_quote_recieved}"
                logging.info(f"GEMINI PROMPT: {gemini_prompt}")
                data = {"contents": [{"parts": [{"text": gemini_prompt}]}]}
            else:
                data = {"contents": [{"parts": [{"text": self.config["gemini_prompt"]}]}]}
            headers = {"Content-Type": "application/json"}
            response = self.ask_gemini(self.gemini_url, headers, data)

            new_quote = self.replace_double_stars_in_response(response)

            if new_quote is None:
                logging.error("Error: No new quote generated")
                continue

            new_quote_text, character = self.extract_quote_and_character(new_quote)

            self.cursor.execute("SELECT quote FROM Quotes")
            existing_quotes = [row[0] for row in self.cursor.fetchall()]

            if all(fuzz.token_sort_ratio(new_quote_text, quote) < 70 for quote in existing_quotes):
                sent_to_twitter = "no"
                sent_to_wordpress = "no"
                sent_to_whatsapp = "no"
                if self.config["send_to_twitter"] == "yes" and self.tweet_quote(new_quote_text, character, self.config["quote_prefix"], self.config["quote_suffix"]):
                    sent_to_twitter = "yes"
                if self.config["send_to_wordpress"] == "yes" and self.create_wp_post(new_quote_text, character, self.config["quote_prefix"], self.config["quote_suffix"]):
                    sent_to_wordpress = "yes"
                if self.config["send_to_whatsapp"] == "yes" and self.send_to_whatsapp(new_quote_text, character, self.config["quote_prefix"], self.config["quote_suffix"]):
                    sent_to_whatsapp = "yes"
                self.cursor.execute("INSERT INTO Quotes (character, quote, date, sent_to_twitter, sent_to_wordpress, sent_to_whatsapp) VALUES (?, ?, ?, ?, ?, ?)", (character, new_quote_text, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sent_to_twitter, sent_to_wordpress, sent_to_whatsapp))
                self.conn.commit()
                break
            else:
                if not duplicate_quote_recieved:
                    duplicate_quote_recieved = "And, give me a quote that is not from the following list: "  # Initialize as a string

                duplicate_quote_recieved += new_quote_text + " ; "

                logging.info(f"Quote already exists in DB, retrying... (attempt {i+1})")
                time.sleep(10)  # Add a delay of 10 seconds before retrying
        else:
            logging.error("Error: Unable to generate a new quote after maximum attempts")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f'Usage: python {sys.argv[0]} <config_file>')
        sys.exit(1)
    config_file = sys.argv[1]
    bot = SocialMediaBot()
    bot.run(config_file)

