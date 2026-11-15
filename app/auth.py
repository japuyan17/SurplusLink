import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .models import Role, User
from .store import store

SECRET = os.getenv("SECRET_KEY", "dev-secret-change-me").encode()
TOKEN_TTL_SECONDS = 12 * 60 * 60
PBKDF2_ROUNDS = 200_000

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ROUNDS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$")
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ROUNDS)
    return hmac.compare_digest(check.hex(), digest)


def _sign(body: str) -> str:
    return hmac.new(SECRET, body.encode(), hashlib.sha256).hexdigest()


def make_token(user_id: int) -> str:
    payload = {"uid": user_id, "exp": int(time.time()) + TOKEN_TTL_SECONDS}
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    return f"{body}.{_sign(body)}"


def read_token(token: str) -> int | None:
    try:
        body, sig = token.split(".")
        if not hmac.compare_digest(sig, _sign(body)):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body))
        return payload["uid"] if payload["exp"] > time.time() else None
    except (ValueError, KeyError, TypeError):
        return None


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> User:
    user = store.users.get(read_token(creds.credentials)) if creds else None
    if not user:
        raise HTTPException(401, "Not authenticated")
    return user


def require_role(role: Role):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role != role:
            raise HTTPException(403, f"This action is for {role}s")
        return user

    return dependency
