"""
Password hashing utilities using bcrypt.

Requirements: 1.1, 1.4
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with 12 salt rounds.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
        
    Requirements: 1.4
    """
    # Generate salt with 12 rounds as per requirements
    salt = bcrypt.gensalt(rounds=12)
    
    # Hash the password
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
        
    Requirements: 1.2
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)
