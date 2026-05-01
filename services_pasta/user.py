from flask import current_app

def encontra_emails_admin(db):
    admins = db.users.find({"is_admin": True})
    return [admin["email"] for admin in admins if "email" in admin]
