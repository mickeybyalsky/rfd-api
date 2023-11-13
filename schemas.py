def individual_serial_user(user) -> dict:
    return {
        "id":str(user["_id"]),
        "user_display_name": user["user_display_name"],
        "user_email": user["user_email"],
        "user_location": user["user_location"]
    }

def list_serial_user(users) -> list:
    return[individual_serial_user(user) for user in users]


def individual_serial_post(post) -> dict:
    return {
        "id":str(post["_id"]),
        "post_title": post["post_title"],
        "post_description": post["post_description"],
        "post_retailer": post["post_retailer"],
        # "post_commet": [list_serial_comment(post["post_comments"])] if post["post_comments"] else "None"
    }

def list_serial_post(posts) -> list:
    return[individual_serial_post(post) for post in posts]

def individual_serial_comment(comment) -> dict:
    return {
        "id":str(comment["_id"]),
        "user_id": comment["user_id"],
        "post_id": comment["post_id"],
        "comment_body": comment["comment_body"]
    }

def list_serial_comment(comments) -> list:
    return[individual_serial_comment(comment) for comment in comments]
