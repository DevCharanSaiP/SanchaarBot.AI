import json
import logging
import base64
from datetime import datetime
from typing import Dict, Any, List
from flask import jsonify
from s3_client import S3Client
from dynamodb_client import DynamoDBClient
import boto3
import uuid

# Initialize clients
s3_client = S3Client()
dynamodb_client = DynamoDBClient()

def handle_document(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle document management operations"""
    
    try:
        action = data.get('action', 'list').lower()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        # Route to appropriate handler
        if action == 'upload':
            return upload_document(user_id, data)
        elif action == 'list':
            return list_documents(user_id)
        elif action == 'download':
            return download_document(user_id, data.get('document_key'))
        elif action == 'delete':
            return delete_document(user_id, data.get('document_key'))
        elif action == 'scan':
            return scan_document_text(user_id, data.get('document_key'))
        elif action == 'organize':
            return organize_documents(user_id)
        else:
            return jsonify({'error': f'Unsupported action: {action}'}), 400
            
    except Exception as e:
        logging.error(f"Error in handle_document: {str(e)}")
        return jsonify({'error': 'Document service error'}), 500

def upload_document(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Upload a document to S3"""
    
    try:
        filename = data.get('filename')
        file_content = data.get('file_content')  # Base64 encoded
        content_type = data.get('content_type', 'application/octet-stream')
        document_type = data.get('document_type', 'other')
        
        if not filename or not file_content:
            return jsonify({'error': 'Missing filename or file_content'}), 400
        
        # Upload to S3
        s3_key = s3_client.upload_base64_document(
            user_id=user_id,
            base64_content=file_content,
            filename=filename,
            content_type=content_type
        )
        
        if not s3_key:
            return jsonify({'error': 'Failed to upload document'}), 500
        
        # Save document metadata to DynamoDB
        document_metadata = {
            'document_id': f"doc_{int(datetime.utcnow().timestamp())}",
            's3_key': s3_key,
            'filename': filename,
            'content_type': content_type,
            'document_type': document_type,
            'uploaded_at': datetime.utcnow().isoformat(),
            'file_size': len(base64.b64decode(file_content)),
            'status': 'uploaded'
        }
        
        # Get user data and add document
        user_data = dynamodb_client.get_user_data(user_id) or {}
        documents = user_data.get('documents', [])
        documents.append(document_metadata)
        user_data['documents'] = documents
        
        success = dynamodb_client.save_user_data(user_id, user_data)
        
        if success:
            return jsonify({
                'message': 'Document uploaded successfully',
                'document': document_metadata
            })
        else:
            return jsonify({'error': 'Failed to save document metadata'}), 500
            
    except Exception as e:
        logging.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': 'Document upload error'}), 500

def list_documents(user_id: str) -> Dict[str, Any]:
    """List all documents for a user"""
    
    try:
        # Get documents from S3
        s3_documents = s3_client.list_user_documents(user_id)
        
        # Get document metadata from DynamoDB
        user_data = dynamodb_client.get_user_data(user_id)
        db_documents = user_data.get('documents', []) if user_data else []
        
        # Merge S3 and DynamoDB data
        documents = []
        
        for s3_doc in s3_documents:
            # Find corresponding metadata
            metadata = next(
                (doc for doc in db_documents if doc.get('s3_key') == s3_doc['key']),
                {}
            )
            
            document = {
                'document_id': metadata.get('document_id', s3_doc['key']),
                's3_key': s3_doc['key'],
                'filename': s3_doc['filename'],
                'document_type': s3_doc['document_type'],
                'size': s3_doc['size'],
                'uploaded_at': s3_doc['upload_timestamp'] or s3_doc['last_modified'],
                'download_url': s3_doc['download_url'],
                'status': metadata.get('status', 'uploaded'),
                'content_type': metadata.get('content_type', 'application/octet-stream')
            }
            
            documents.append(document)
        
        # Sort by upload date (newest first)
        documents.sort(key=lambda x: x['uploaded_at'], reverse=True)
        
        # Group documents by type
        grouped_documents = {}
        for doc in documents:
            doc_type = doc['document_type']
            if doc_type not in grouped_documents:
                grouped_documents[doc_type] = []
            grouped_documents[doc_type].append(doc)
        
        return jsonify({
            'documents': documents,
            'grouped_documents': grouped_documents,
            'count': len(documents),
            'types': list(grouped_documents.keys())
        })
        
    except Exception as e:
        logging.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': 'Document list error'}), 500

def download_document(user_id: str, document_key: str) -> Dict[str, Any]:
    """Generate download URL for a document"""
    
    try:
        if not document_key:
            return jsonify({'error': 'Missing document_key'}), 400
        
        # Verify user owns the document
        if not document_key.startswith(f"documents/{user_id}/"):
            return jsonify({'error': 'Access denied'}), 403
        
        # Generate presigned URL
        download_url = s3_client.get_document_url(document_key, expires_in=3600)
        
        if download_url:
            # Get document metadata
            user_data = dynamodb_client.get_user_data(user_id)
            documents = user_data.get('documents', []) if user_data else []
            
            document_metadata = next(
                (doc for doc in documents if doc.get('s3_key') == document_key),
                {}
            )
            
            return jsonify({
                'download_url': download_url,
                'expires_in_seconds': 3600,
                'document_metadata': document_metadata
            })
        else:
            return jsonify({'error': 'Failed to generate download URL'}), 500
            
    except Exception as e:
        logging.error(f"Error downloading document: {str(e)}")
        return jsonify({'error': 'Document download error'}), 500

def delete_document(user_id: str, document_key: str) -> Dict[str, Any]:
    """Delete a document"""
    
    try:
        if not document_key:
            return jsonify({'error': 'Missing document_key'}), 400
        
        # Verify user owns the document
        if not document_key.startswith(f"documents/{user_id}/"):
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete from S3
        s3_success = s3_client.delete_document(document_key)
        
        if not s3_success:
            return jsonify({'error': 'Failed to delete document from storage'}), 500
        
        # Remove from DynamoDB metadata
        user_data = dynamodb_client.get_user_data(user_id)
        if user_data and 'documents' in user_data:
            documents = user_data['documents']
            user_data['documents'] = [
                doc for doc in documents if doc.get('s3_key') != document_key
            ]
            
            dynamodb_client.save_user_data(user_id, user_data)
        
        return jsonify({
            'message': 'Document deleted successfully',
            'document_key': document_key
        })
        
    except Exception as e:
        logging.error(f"Error deleting document: {str(e)}")
        return jsonify({'error': 'Document deletion error'}), 500

def scan_document_text(user_id: str, document_key: str) -> Dict[str, Any]:
    """Extract text from document using AWS Textract"""
    
    try:
        if not document_key:
            return jsonify({'error': 'Missing document_key'}), 400
        
        # Verify user owns the document
        if not document_key.startswith(f"documents/{user_id}/"):
            return jsonify({'error': 'Access denied'}), 403
        
        # Initialize Textract client
        textract_client = boto3.client('textract')
        
        try:
            # Use Textract to extract text
            response = textract_client.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': s3_client.bucket_name,
                        'Name': document_key
                    }
                }
            )
            
            # Extract text from response
            extracted_text = ""
            confidence_scores = []
            
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    extracted_text += block.get('Text', '') + "\n"
                    confidence_scores.append(block.get('Confidence', 0))
            
            # Calculate average confidence
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            # Save extracted text to user data
            user_data = dynamodb_client.get_user_data(user_id) or {}
            extractions = user_data.get('document_extractions', [])
            
            extraction_data = {
                'extraction_id': f"extract_{int(datetime.utcnow().timestamp())}",
                'document_key': document_key,
                'extracted_text': extracted_text,
                'confidence': avg_confidence,
                'extracted_at': datetime.utcnow().isoformat(),
                'word_count': len(extracted_text.split())
            }
            
            extractions.append(extraction_data)
            user_data['document_extractions'] = extractions[-20:]  # Keep last 20
            
            dynamodb_client.save_user_data(user_id, user_data)
            
            return jsonify({
                'extracted_text': extracted_text,
                'confidence': avg_confidence,
                'word_count': len(extracted_text.split()),
                'extraction_id': extraction_data['extraction_id']
            })
            
        except Exception as textract_error:
            # Fallback for unsupported file types
            return jsonify({
                'error': 'Text extraction not supported for this file type',
                'details': str(textract_error)
            }), 400
            
    except Exception as e:
        logging.error(f"Error scanning document: {str(e)}")
        return jsonify({'error': 'Document scan error'}), 500

def organize_documents(user_id: str) -> Dict[str, Any]:
    """Organize documents by type and create folders"""
    
    try:
        # Get all user documents
        documents_response = list_documents(user_id)
        documents_data = json.loads(documents_response.data)
        
        if 'documents' not in documents_data:
            return jsonify({'message': 'No documents to organize'})
        
        documents = documents_data['documents']
        
        # Organization statistics
        organization_stats = {
            'total_documents': len(documents),
            'by_type': {},
            'by_month': {},
            'total_size': 0
        }
        
        for doc in documents:
            # Count by type
            doc_type = doc['document_type']
            organization_stats['by_type'][doc_type] = organization_stats['by_type'].get(doc_type, 0) + 1
            
            # Count by upload month
            upload_date = datetime.fromisoformat(doc['uploaded_at'].replace('Z', '+00:00'))
            month_key = upload_date.strftime('%Y-%m')
            organization_stats['by_month'][month_key] = organization_stats['by_month'].get(month_key, 0) + 1
            
            # Total size
            organization_stats['total_size'] += doc.get('size', 0)
        
        # Create document tags based on content (simplified)
        tagged_documents = []
        for doc in documents:
            tags = []
            filename_lower = doc['filename'].lower()
            
            # Auto-tag based on filename patterns
            if any(word in filename_lower for word in ['ticket', 'boarding', 'flight']):
                tags.append('travel_tickets')
            if any(word in filename_lower for word in ['hotel', 'booking', 'reservation']):
                tags.append('accommodation')
            if any(word in filename_lower for word in ['passport', 'visa', 'id']):
                tags.append('identification')
            if any(word in filename_lower for word in ['insurance', 'policy']):
                tags.append('insurance')
            
            doc['tags'] = tags
            tagged_documents.append(doc)
        
        # Update user data with organized documents
        user_data = dynamodb_client.get_user_data(user_id) or {}
        user_data['documents_organized'] = {
            'organized_at': datetime.utcnow().isoformat(),
            'organization_stats': organization_stats,
            'tagged_documents': tagged_documents
        }
        
        dynamodb_client.save_user_data(user_id, user_data)
        
        return jsonify({
            'message': 'Documents organized successfully',
            'organization_stats': organization_stats,
            'recommendations': generate_organization_recommendations(organization_stats)
        })
        
    except Exception as e:
        logging.error(f"Error organizing documents: {str(e)}")
        return jsonify({'error': 'Document organization error'}), 500

def generate_organization_recommendations(stats: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on document organization stats"""
    
    recommendations = []
    
    # Check for document types
    if stats['by_type'].get('other', 0) > 5:
        recommendations.append("Consider categorizing your 'other' documents with more specific types")
    
    if stats['by_type'].get('identification', 0) > 0:
        recommendations.append("Make sure your identification documents are up to date")
    
    if stats['total_size'] > 100 * 1024 * 1024:  # 100MB
        recommendations.append("Consider creating backups of your documents")
    
    if len(stats['by_month']) > 6:
        recommendations.append("You might want to archive older documents to keep your active documents organized")
    
    return recommendations

def create_document_backup(user_id: str) -> Dict[str, Any]:
    """Create a backup of all user documents"""
    
    try:
        backup_key = s3_client.create_backup(user_id)
        
        if backup_key:
            # Generate download URL for backup
            download_url = s3_client.get_document_url(backup_key, expires_in=86400)  # 24 hours
            
            return jsonify({
                'message': 'Document backup created successfully',
                'backup_key': backup_key,
                'download_url': download_url,
                'expires_in_hours': 24
            })
        else:
            return jsonify({'error': 'Failed to create backup'}), 500
            
    except Exception as e:
        logging.error(f"Error creating document backup: {str(e)}")
        return jsonify({'error': 'Document backup error'}), 500

def share_document(data: Dict[str, Any]) -> Dict[str, Any]:
    """Share a document with others"""
    
    try:
        user_id = data.get('user_id')
        document_key = data.get('document_key')
        expiry_hours = data.get('expiry_hours', 24)
        
        if not user_id or not document_key:
            return jsonify({'error': 'Missing user_id or document_key'}), 400
        
        # Verify user owns the document
        if not document_key.startswith(f"documents/{user_id}/"):
            return jsonify({'error': 'Access denied'}), 403
        
        # Generate shareable URL
        share_url = s3_client.get_document_url(document_key, expires_in=expiry_hours * 3600)
        
        if share_url:
            # Log the share activity
            user_data = dynamodb_client.get_user_data(user_id) or {}
            shared_documents = user_data.get('shared_documents', [])
            
            share_record = {
                'document_key': document_key,
                'shared_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat(),
                'share_id': f"share_{int(datetime.utcnow().timestamp())}"
            }
            
            shared_documents.append(share_record)
            user_data['shared_documents'] = shared_documents[-10:]  # Keep last 10
            
            dynamodb_client.save_user_data(user_id, user_data)
            
            return jsonify({
                'share_url': share_url,
                'expires_in_hours': expiry_hours,
                'share_id': share_record['share_id']
            })
        else:
            return jsonify({'error': 'Failed to generate share URL'}), 500
            
    except Exception as e:
        logging.error(f"Error sharing document: {str(e)}")
        return jsonify({'error': 'Document sharing error'}), 500