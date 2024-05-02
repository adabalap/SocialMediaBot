import tweepy
import logging

def setup_twitter(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret):
    """
    Sets up the Twitter API.
    """
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth)
    return api

def tweet_quote(api, quote, character, quote_prefix, quote_suffix):
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
        api.update_status(tweet)
        logging.info("Tweet sent!")
        return True
    except Exception as e:
        logging.error(f"Error while tweeting: {str(e)}")
        return False

