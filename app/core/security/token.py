# 密码哈希（PBKDF2）与 JWT 登录令牌（HS256，标准库实现）
import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Optional

from app.core.config.settings import SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "base-fastapi"
TOKEN_EXPIRE_SECONDS = 12 * 3600
PBKDF2_ROUNDS = 120000


def _b64url_encode(raw: bytes) -> str:
    """JWT 规定的 Base64URL，去掉填充符。"""
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(text: str) -> bytes:
    """还原 Base64URL。"""
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def hash_password(password: str) -> str:
    """PBKDF2-SHA256 哈希，格式 pbkdf2$轮次$盐$摘要。"""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS)
    return f"pbkdf2${PBKDF2_ROUNDS}${_b64url_encode(salt)}${_b64url_encode(digest)}"


def verify_password(password: str, stored: str) -> bool:
    """校验明文密码是否匹配已存哈希。"""
    try:
        algo, rounds, salt_b64, digest_b64 = stored.split("$", 3)
        if algo != "pbkdf2":
            return False
        salt = _b64url_decode(salt_b64)
        expect = _b64url_decode(digest_b64)
        got = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(rounds))
        return hmac.compare_digest(got, expect)
    except Exception:
        return False


def _jwt_sign(signing_input: bytes) -> str:
    """HS256：HMAC-SHA256 后做 Base64URL。"""
    digest = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return _b64url_encode(digest)


def create_token(user_id: int, username: str) -> str:
    """
    签发 JWT：header.payload.signature。
    声明含 sub/uid/un/iat/exp/iss。
    """
    now = int(time.time())
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "uid": user_id,
        "un": username,
        "iat": now,
        "exp": now + TOKEN_EXPIRE_SECONDS,
        "iss": JWT_ISSUER,
    }
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    return f"{header_b64}.{payload_b64}.{_jwt_sign(signing_input)}"


def parse_token(token: str) -> Optional[dict[str, Any]]:
    """校验 JWT 头、签名、过期时间和签发方；失败返回 None。"""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig = parts
        header = json.loads(_b64url_decode(header_b64).decode("utf-8"))
        if header.get("alg") != JWT_ALGORITHM or header.get("typ") != "JWT":
            return None
        expect = _jwt_sign(f"{header_b64}.{payload_b64}".encode("ascii"))
        if not hmac.compare_digest(expect, sig):
            return None
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        if payload.get("iss") != JWT_ISSUER:
            return None
        if int(payload.get("exp") or 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
