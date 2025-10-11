import boto3
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError
import base64

class S3Client:
    """Client for managing S3 operations for travel documents and files"""
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'travel-companion-agent-bucket'
        
    def upload_document(self, user_id: str, file_content: bytes, 
                       filename: str, content_type: str = 'application/octet-stream') -> Optional[str]:
        """Upload a travel document to S3"""
        try:
            # Generate unique file key
            file_extension = filename.split('.')[-1] if '.' in filename else 'bin'
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            key = f"documents/{user_id}/{unique_filename}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'user_id': user_id,
                    'original_filename': filename,
                    'upload_timestamp': datetime.utcnow().isoformat(),
                    'document_type': self._classify_document_type(filename)
                }
            )
            
            logging.info(f"Document uploaded successfully: {key}")
            return key
            
        except ClientError as e:
            logging.error(f"Error uploading document: {e}")
            return None
    
    def upload_base64_document(self, user_id: str, base64_content: str, 
                              filename: str, content_type: str = 'application/octet-stream') -> Optional[str]:
        """Upload a base64 encoded document to S3"""
        try:
            # Decode base64 content
            file_content = base64.b64decode(base64_content)
            return self.upload_document(user_id, file_content, filename, content_type)
            
        except Exception as e:
            logging.error(f"Error uploading base64 document: {e}")
            return None
    
    def download_document(self, key: str) -> Optional[Dict[str, Any]]:
        """Download a document from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            
            return {
                'content': response['Body'].read(),
                'content_type': response.get('ContentType', 'application/octet-stream'),
                'metadata': response.get('Metadata', {}),
                'last_modified': response.get('LastModified'),
                'size': response.get('ContentLength', 0)
            }
            
        except ClientError as e:
            logging.error(f"Error downloading document: {e}")
            return None
    
    def get_document_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a presigned URL for document access"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
            
        except ClientError as e:
            logging.error(f"Error generating presigned URL: {e}")
            return None
    
    def list_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """List all documents for a specific user"""
        try:
            prefix = f"documents/{user_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            documents = []
            for obj in response.get('Contents', []):
                # Get object metadata
                head_response = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
                
                documents.append({
                    'key': obj['Key'],
                    'filename': head_response.get('Metadata', {}).get('original_filename', 'Unknown'),
                    'document_type': head_response.get('Metadata', {}).get('document_type', 'unknown'),
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'upload_timestamp': head_response.get('Metadata', {}).get('upload_timestamp', ''),
                    'download_url': self.get_document_url(obj['Key'])
                })
                
            return documents
            
        except ClientError as e:
            logging.error(f"Error listing user documents: {e}")
            return []
    
    def delete_document(self, key: str) -> bool:
        """Delete a document from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logging.info(f"Document deleted successfully: {key}")
            return True
            
        except ClientError as e:
            logging.error(f"Error deleting document: {e}")
            return False
    
    def save_itinerary_pdf(self, user_id: str, pdf_content: bytes) -> Optional[str]:
        """Save generated itinerary PDF"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            key = f"itineraries/{user_id}/itinerary_{timestamp}.pdf"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=pdf_content,
                ContentType='application/pdf',
                Metadata={
                    'user_id': user_id,
                    'document_type': 'itinerary',
                    'generated_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            return key
            
        except ClientError as e:
            logging.error(f"Error saving itinerary PDF: {e}")
            return None
    
    def save_booking_confirmation(self, user_id: str, booking_data: Dict[str, Any]) -> Optional[str]:
        """Save booking confirmation as JSON"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            booking_type = booking_data.get('type', 'unknown')
            key = f"bookings/{user_id}/{booking_type}_confirmation_{timestamp}.json"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(booking_data, indent=2),
                ContentType='application/json',
                Metadata={
                    'user_id': user_id,
                    'document_type': 'booking_confirmation',
                    'booking_type': booking_type,
                    'generated_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            return key
            
        except ClientError as e:
            logging.error(f"Error saving booking confirmation: {e}")
            return None
    
    def _classify_document_type(self, filename: str) -> str:
        """Classify document type based on filename"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['passport', 'visa', 'id']):
            return 'identification'
        elif any(word in filename_lower for word in ['ticket', 'boarding', 'flight']):
            return 'flight_document'
        elif any(word in filename_lower for word in ['hotel', 'reservation', 'booking']):
            return 'accommodation'
        elif any(word in filename_lower for word in ['insurance', 'policy']):
            return 'insurance'
        elif any(word in filename_lower for word in ['itinerary', 'plan', 'schedule']):
            return 'itinerary'
        else:
            return 'other'
    
    def create_backup(self, user_id: str) -> Optional[str]:
        """Create a backup of all user documents"""
        try:
            import zipfile
            import io
            
            # Create in-memory zip file
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Get all user documents
                documents = self.list_user_documents(user_id)
                
                for doc in documents:
                    # Download document content
                    doc_data = self.download_document(doc['key'])
                    if doc_data:
                        zip_file.writestr(doc['filename'], doc_data['content'])
            
            # Upload zip file
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_key = f"backups/{user_id}/backup_{timestamp}.zip"
            
            zip_buffer.seek(0)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=backup_key,
                Body=zip_buffer.getvalue(),
                ContentType='application/zip',
                Metadata={
                    'user_id': user_id,
                    'document_type': 'backup',
                    'backup_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            return backup_key
            
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return None
    
    def cleanup_old_documents(self, user_id: str, days_old: int = 90) -> int:
        """Clean up old documents for a user"""
        try:
            cutoff_date = datetime.utcnow().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            # List all user documents
            prefix = f"documents/{user_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            for obj in response.get('Contents', []):
                if obj['LastModified'].timestamp() < cutoff_date:
                    self.delete_document(obj['Key'])
                    deleted_count += 1
            
            logging.info(f"Cleaned up {deleted_count} old documents for user {user_id}")
            return deleted_count
            
        except Exception as e:
            logging.error(f"Error cleaning up old documents: {e}")
            return 0
    
    def ensure_bucket_exists(self) -> bool:
        """Ensure the S3 bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                try:
                    # Create bucket
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    
                    # Set up bucket policies for security
                    bucket_policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "RestrictToApplication",
                                "Effect": "Deny",
                                "Principal": "*",
                                "Action": "s3:*",
                                "Resource": [
                                    f"arn:aws:s3:::{self.bucket_name}",
                                    f"arn:aws:s3:::{self.bucket_name}/*"
                                ],
                                "Condition": {
                                    "StringNotEquals": {
                                        "aws:PrincipalServiceName": ["lambda.amazonaws.com", "ec2.amazonaws.com"]
                                    }
                                }
                            }
                        ]
                    }
                    
                    self.s3_client.put_bucket_policy(
                        Bucket=self.bucket_name,
                        Policy=json.dumps(bucket_policy)
                    )
                    
                    # Enable encryption
                    self.s3_client.put_bucket_encryption(
                        Bucket=self.bucket_name,
                        ServerSideEncryptionConfiguration={
                            'Rules': [
                                {
                                    'ApplyServerSideEncryptionByDefault': {
                                        'SSEAlgorithm': 'AES256'
                                    }
                                }
                            ]
                        }
                    )
                    
                    return True
                    
                except ClientError as create_error:
                    logging.error(f"Error creating bucket: {create_error}")
                    return False
            else:
                logging.error(f"Error checking bucket: {e}")
                return False