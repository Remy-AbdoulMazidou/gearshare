import hashlib
import hmac
import secrets


ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, ITERATIONS
    )
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(plain: str, stored: str) -> bool:
    if not isinstance(stored, str):
        return False

    try:
        algorithm, iterations_text, salt_hex, expected_hex = stored.split("$")
        iterations = int(iterations_text)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(expected_hex)
    except (AttributeError, TypeError, ValueError, OverflowError):
        return False

    if algorithm != ALGORITHM or iterations <= 0:
        return False

    try:
        digest = hashlib.pbkdf2_hmac(
            "sha256", plain.encode(), salt, iterations
        )
    except (TypeError, ValueError, OverflowError):
        return False

    return hmac.compare_digest(digest, expected)
