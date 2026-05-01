import hashlib
import secrets


def hash_password(password: str) -> str:
    iterations = 260000
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algo, iterations, salt, expected = stored_hash.split("$")
        if algo != "pbkdf2_sha256":
            return False

        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )

        return secrets.compare_digest(dk.hex(), expected)
    except Exception:
        return False