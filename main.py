import sys
import time
import logging
from rapidfuzz import fuzz, process
from datetime import datetime
from config import load_config
from database import setup_db
from logging_config import setup_logging
from twitter_handler import setup_twitter, tweet_quote
from wordpress_handler import create_wp_post
from whatsapp_handler import setup_whatsapp, send_to_whatsapp
from gemini_handler import setup_gemini, ask_gemini, replace_double_stars_in_response, extract_quote_and_character

class SocialMediaBot:
    def __init__(self, config):
        self.config = config
        self.conn, self.cursor = setup_db(config["db_file"])
        self.twitter_api = setup_twitter(config["twitter_consumer_key"], config["twitter_consumer_secret"], config["twitter_access_token"], config["twitter_access_token_secret"])
        self.gemini_url = setup_gemini(config['gemini_api'], config['gemini_api_key'])
        self.whatsapp_api_url, self.whatsapp_api_headers_dict, self.whatsapp_api_key = setup_whatsapp(config["whatsapp_api_url"], config["whatsapp_api_key"])

    def run(self):
        duplicate_quote_recieved = ""

        for i in range(self.config["max_gemini_attempts"]):
            if duplicate_quote_recieved:
                gemini_prompt = f"{self.config['gemini_prompt']} {duplicate_quote_recieved}"
                logging.info(f"GEMINI PROMPT: {gemini_prompt}")
                data = {"contents": [{"parts": [{"text": gemini_prompt}]}]}
            else:
                data = {"contents": [{"parts": [{"text": self.config["gemini_prompt"]}]}]}
            headers = {"Content-Type": "application/json"}
            response = ask_gemini(self.gemini_url, headers, data)

            new_quote = replace_double_stars_in_response(response)
            if new_quote is None:
                logging.error("Error: No new quote generated")
                continue

            new_quote_text, character = extract_quote_and_character(new_quote)

            self.cursor.execute("SELECT quote FROM Quotes")
            existing_quotes = [row[0] for row in self.cursor.fetchall()]

            if all(fuzz.token_sort_ratio(new_quote_text, quote) < 70 for quote in existing_quotes):
                logging.debug(f"Checking if the quote already exists in the DB...")
                sent_to_twitter = "no"
                sent_to_wordpress = "no"
                sent_to_whatsapp = "no"

                if self.config["send_to_twitter"] == "yes" and tweet_quote(self.twitter_api, new_quote_text, character, self.config["quote_prefix"], self.config["quote_suffix"]):
                    sent_to_twitter = "yes"
                if self.config["send_to_wordpress"] == "yes" and create_wp_post(self.config, new_quote_text, character, self.config["quote_prefix"], self.config["quote_suffix"]):
                    sent_to_wordpress = "yes"
                if self.config["send_to_whatsapp"] == "yes" and send_to_whatsapp(self.config, new_quote_text, character, self.config["quote_prefix"], self.config["quote_suffix"]):
                    sent_to_whatsapp = "yes"

                self.cursor.execute("INSERT INTO Quotes (character, quote, date, sent_to_twitter, sent_to_wordpress, sent_to_whatsapp) VALUES (?, ?, ?, ?, ?, ?)", (character, new_quote_text, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sent_to_twitter, sent_to_wordpress, sent_to_whatsapp))
                self.conn.commit()
                break
            else:
                if not duplicate_quote_recieved:
                    duplicate_quote_recieved = ". Ensure, the new quote isn't from the following list of quote's: "  # Initialize as a string

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
    config = load_config(config_file)
    setup_logging(config["log_file"], config["logging_level"])
    bot = SocialMediaBot(config)
    bot.run()

