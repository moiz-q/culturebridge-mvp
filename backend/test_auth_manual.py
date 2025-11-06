"""
Manual test script for authentication system.
Run this to verify the authentication implementation works.

Usage:
    python test_auth_manual.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.password import hash_password, verify_password
from app.utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
    create_password_reset_token,
    verify_password_reset_token,
    JWTError
)


def test_password_hashing():
    """Test password hashing and verification"""
    print("\n=== Testing Password Hashing ===")
    
    password = "testpassword123"
    print(f"Original password: {password}")
    
    # Hash password
    hashed = hash_password(password)
    print(f"Hashed password: {hashed[:50]}...")
    
    # Verify correct password
    is_valid = verify_password(password, hashed)
    print(f"Verify correct password: {is_valid}")
    assert is_valid, "Password verification failed!"
    
    # Verify wrong password
    is_valid = verify_password("wrongpassword", hashed)
    print(f"Verify wrong password: {is_valid}")
    assert not is_valid, "Wrong password should not verify!"
    
    print("✅ Password hashing tests passed!")


def test_jwt_tokens():
    """Test JWT token generation and verification"""
    print("\n=== Testing JWT Tokens ===")
    
    user_data = {
        "sub": "123e4567-e89b-12d3-a456-426614174000",
        "email": "test@example.com",
        "role": "client"
    }
    
    # Create access token
    access_token = create_access_token(user_data)
    print(f"Access token created: {access_token[:50]}...")
    
    # Verify access token
    payload = verify_token(access_token)
    print(f"Token payload: {payload}")
    assert payload["sub"] == user_data["sub"], "User ID mismatch!"
    assert payload["email"] == user_data["email"], "Email mismatch!"
    assert payload["role"] == user_data["role"], "Role mismatch!"
    
    # Create refresh token
    refresh_token = create_refresh_token(user_data)
    print(f"Refresh token created: {refresh_token[:50]}...")
    
    # Verify refresh token
    from app.utils.jwt_utils import verify_refresh_token
    refresh_payload = verify_refresh_token(refresh_token)
    print(f"Refresh token payload: {refresh_payload}")
    assert refresh_payload["type"] == "refresh", "Token type mismatch!"
    
    print("✅ JWT token tests passed!")


def test_password_reset_token():
    """Test password reset token"""
    print("\n=== Testing Password Reset Token ===")
    
    email = "test@example.com"
    
    # Create reset token
    reset_token = create_password_reset_token(email)
    print(f"Reset token created: {reset_token[:50]}...")
    
    # Verify reset token
    extracted_email = verify_password_reset_token(reset_token)
    print(f"Extracted email: {extracted_email}")
    assert extracted_email == email, "Email mismatch!"
    
    print("✅ Password reset token tests passed!")


def test_invalid_token():
    """Test invalid token handling"""
    print("\n=== Testing Invalid Token Handling ===")
    
    invalid_token = "invalid.token.here"
    
    try:
        verify_token(invalid_token)
        print("❌ Should have raised JWTError!")
        assert False, "Invalid token should raise error!"
    except JWTError as e:
        print(f"✅ Correctly raised JWTError: {e}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Authentication System Manual Tests")
    print("=" * 60)
    
    try:
        test_password_hashing()
        test_jwt_tokens()
        test_password_reset_token()
        test_invalid_token()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nAuthentication system is working correctly!")
        print("\nNext steps:")
        print("1. Start the FastAPI server: uvicorn app.main:app --reload")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Test the endpoints using the interactive docs")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
