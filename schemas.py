from models import UserOut


def individual_serial_user(user):
    user_counts =  {"user_reputation": user.get("user_reputation", 0),
        "user_post_count": user.get("user_post_count", 0),
        "user_comment_count": user.get("user_comment_count", 0)
    }
    return {
        "user_id": str(user.get("_id", "")),
        "user_name": user.get("username", ""),
        "user_email": user.get("user_email", ""),
        "user_full_name": user.get("user_full_name", ""),
        "user_location": user.get("user_location", ""),
        "user_join_date": user.get("user_join_date", ""),
        "user_role": user.get("user_role", ""),
        "user_activity": user_counts
    }
    
def list_serial_user(users):
    return {str(user["username"]): individual_serial_user(user) for user in users}

def individual_serial_post(post):
    return {
            "post_title": post.get("post_title", ""),
            "post_description": post.get("post_description", ""),
            "post_product_category": post.get("post_product_category", ""),
            "post_link_to_deal": post.get("post_link_to_deal", ""),
            "post_deal_expiry": post.get("post_deal_expiry", ""),
            "post_sale_price": post.get("post_sale_price", ""),
            "post_product_discount": post.get("post_product_discount", ""),
            "post_votes": post.get("post_votes", 0),
            "post_timestamp": post.get("post_timestamp", ""),
            "post_author": post.get("post_author", ""),
            "post_views": post.get("post_views", 0)
    }

def list_serial_post(posts) -> list:
    return {str(post["_id"]): individual_serial_post(post) for post in posts}

def individual_serial_comment(comment):
    return {
        # "post_id": comment.get("comment_post_id", ""),
        "comment_author": comment.get("comment_author", ""),
        "comment_body": comment.get("comment_body"),
        "comment_votes": comment.get("comment_votes", None),
        "comment_timestamp": comment.get("comment_timestamp", None)
    }

def list_serial_comment(comments) -> list:
    return {str(comment["_id"]): individual_serial_comment(comment) for comment in comments}