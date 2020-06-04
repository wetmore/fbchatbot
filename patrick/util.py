import json

import fbchat


SESSION_FILE = "session.json"


def save_session(session):
    with open(SESSION_FILE, "w") as f:
        json.dump(session.get_cookies(), f)


def get_session(config):
    try:
        # Load cookies from file
        with open(SESSION_FILE) as f:
            cookies = json.load(f)
        session = fbchat.Session.from_cookies(cookies)
        status = "Loaded session from saved cookies"
    except (FileNotFoundError, fbchat.FacebookError):
        session = fbchat.Session.login(config.BOT_EMAIL, config.BOT_PASSWORD)
        status = "Created new session"
    return session, status
