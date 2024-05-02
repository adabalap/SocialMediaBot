import xmlrpc.client
import logging

def create_wp_post(config, quote, character, quote_prefix, quote_suffix):
    """
    Creates a new WordPress post with the successfully posted Twitter message.
    """
    if character:
        wp_update = f"{quote_prefix} {quote} - {character}"
    else:
        wp_update = f"{quote_prefix} {quote}"
    try:
        wp_url = config["wp_url"]
        wp_username = config["wp_username"]
        wp_password = config["wp_password"]
        wp_category = config["wp_category"]

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

