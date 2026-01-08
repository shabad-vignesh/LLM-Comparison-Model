import time
USER_LIMIT = {}
MAX_REQUESTS = 10
WINDOW = 60
def check_limit(user):
    now = time.time()
    USER_LIMIT.setdefault(user, [])
    USER_LIMIT[user] = [t for t in USER_LIMIT[user] if now - t < WINDOW]
    if len(USER_LIMIT[user]) >= MAX_REQUESTS:
        return False
    USER_LIMIT[user].append(now)
    return True



