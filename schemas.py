def individual_serial_user(user):
    return {
        "id":str(user["_id"]),
        "user_display_name": user["user_display_name"],
        "user_email": user["user_email"],
        "user_location": user["user_location"]
    }

def list_serial_user(users):
    return[individual_serial_user(user) for user in users]


def individual_serial_post(post):
    return {
        "id":str(post["_id"]),
        "post_title": post["post_title"],
        "post_description": post["post_description"],
        "post_retailer": post.get("post_retailer"),
        "post_votes": post.get("post_votes"),
        "post_timestamp": post.get("post_timestamp")
    }

def list_serial_post(posts) -> list:
    return[individual_serial_post(post) for post in posts]

def individual_serial_comment(comment):
    return {
        "id":str(comment.get("_id")),
        "user_id": comment.get("user_id"),
        "post_id": comment.get("post_id"),
        "comment_body": comment.get("comment_body"),
        "comment_votes": comment.get("comment_votes", None),
        "comment_timestamp": comment.get("comment_timestamp", None)
    }

def list_serial_comment(comments) -> list:
    return[individual_serial_comment(comment) for comment in comments]
