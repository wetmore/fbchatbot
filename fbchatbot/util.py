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


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @classmethod
    def yellow(cls, string):
        return f"{cls.YELLOW}{string}{cls.ENDC}"

    @classmethod
    def green(cls, string):
        return f"{cls.GREEN}{string}{cls.ENDC}"

    @classmethod
    def blue(cls, string):
        return f"{cls.BLUE}{string}{cls.ENDC}"
