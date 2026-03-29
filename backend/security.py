from datetime import datetime, timedelta
import jwt 
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE"))

def get_password_hash(password: str) -> str:
    """Converts a plain password into a secure bcrypt hash."""
    # Bcrypt requires bytes, so we encode the string to utf-8 first
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8') # Decode back to a string for the database


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the plain password matches the encrypted hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Generates the JWT (JSON Web Token)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt