from datetime import datetime, timezone


def create_user_document(
    name: str,
    email: str,
    password_hash: str
):
    """
    Create a MongoDB document for a user.
    """

    if not name or not name.strip():
        raise ValueError("Name cannot be empty")

    if not email or not email.strip():
        raise ValueError("Email cannot be empty")

    if not password_hash or not password_hash.strip():
        raise ValueError("Password hash cannot be empty")

    return {
        "name": name.strip(),
        "email": email.strip().lower(),
        "password_hash": password_hash,
        "created_at": datetime.now(timezone.utc),
    }