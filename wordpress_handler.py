import requests
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
        wp_token = config["wp_token"]  # This should be your JWT token
        wp_category_id = config["wp_category_id"]  # This should be your category ID

        post = {
            "title": wp_update[:40] + "...",  # Use the first 40 characters of the update as the post title
            "content": wp_update,
            "status": "publish",
            "categories": [wp_category_id]  # The category ID of the post
        }

        response = requests.post(f"{wp_url}/wp-json/wp/v2/posts", headers={"Authorization": f"Bearer {wp_token}"}, json=post)

        if response.status_code == 201:
            logging.info(f"WordPress post created with ID: {response.json()['id']}!")
            return True
        else:
            logging.error(f"Error while creating WordPress post: {response.json()}")
            return False
    except Exception as e:
        logging.error(f"Error while creating WordPress post: {str(e)}")
        return False
