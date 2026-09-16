import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    """

    if not password:
        raise ValueError("Password cannot be empty")

    password_bytes = password.encode("utf-8")

    password_hash = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return password_hash.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str
) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """

    if not password:
        raise ValueError("Password cannot be empty")

    if not password_hash:
        raise ValueError("Password hash cannot be empty")

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )