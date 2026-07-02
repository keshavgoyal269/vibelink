import bcrypt
import streamlit as st
from src.database import get_user_by_email, create_user


def hash_password(password: str) -> str:
    """Securely hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    """Check a plain password against a stored hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def login_user(email: str, password: str):
    """
    Attempts to log in. Returns user row if successful, None if not.
    Also sets st.session_state so the rest of the app knows who's logged in.
    """
    user = get_user_by_email(email)
    if user and check_password(password, user["password_hash"]):
        st.session_state["user_id"] = user["id"]
        st.session_state["user_name"] = user["name"]
        return user
    return None


def register_user(name, email, password, age, city, bio):
    """
    Registers a new user. Returns True if successful, False if email taken.
    """
    password_hash = hash_password(password)
    return create_user(name, email, password_hash, age, city, bio)


def logout_user():
    """Clears session state — effectively logs the user out."""
    for key in ["user_id", "user_name"]:
        if key in st.session_state:
            del st.session_state[key]


def is_logged_in() -> bool:
    """Quick check — is there an active session?"""
    return "user_id" in st.session_state