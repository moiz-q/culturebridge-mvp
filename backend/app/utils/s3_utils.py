"""
AWS S3 utilities for file upload and management.

Requirements: 2.3
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple
import uuid
import mimetypes
from io import BytesIO

from app.config import settings


class S3Service:
    """Service for AWS S3 file operations"""
    
    # Allowed image formats (5MB max, JPEG/PNG/WebP)
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = None
        self.bucket_name = settings.S3_BUCKET_NAME
        
        # Only initialize if AWS credentials are configured
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                's3',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
    
    def validate_image(self, file_content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate image file size and format.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if len(file_content) > self.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024 * 1024)}MB"
        
        # Check file extension
        file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File format not allowed. Allowed formats: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type not in self.ALLOWED_MIME_TYPES:
            return False, f"Invalid file type. Allowed types: JPEG, PNG, WebP"
        
        return True, None
    
    def upload_profile_photo(
        self,
        file_content: bytes,
        filename: str,
        user_id: str
    ) -> Optional[str]:
        """
        Upload profile photo to S3.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            user_id: User ID for organizing files
        
        Returns:
            S3 URL of uploaded file or None if upload fails
        
        Raises:
            ValueError: If file validation fails
            Exception: If S3 upload fails
        """
        # Validate image
        is_valid, error_message = self.validate_image(file_content, filename)
        if not is_valid:
            raise ValueError(error_message)
        
        # Check if S3 is configured
        if not self.s3_client or not self.bucket_name:
            raise Exception("S3 is not configured. Please set AWS credentials and bucket name.")
        
        # Generate unique filename
        file_ext = filename.rsplit('.', 1)[-1].lower()
        unique_filename = f"profiles/{user_id}/{uuid.uuid4()}.{file_ext}"
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(filename)
        
        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'  # Make file publicly accessible
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            return url
            
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete file from S3.
        
        Args:
            file_url: Full S3 URL of the file
        
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.s3_client or not self.bucket_name:
            return False
        
        try:
            # Extract key from URL
            # URL format: https://bucket.s3.region.amazonaws.com/key
            key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError:
            return False


# Singleton instance
s3_service = S3Service()
