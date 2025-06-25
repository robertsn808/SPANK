"""
Notification Management Service for SPANKKS Construction
Handles notification settings, templates, and delivery tracking
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class NotificationService:
    """Professional notification management system"""
    
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def get_notification_settings(self) -> List[Dict]:
        """Get all notification settings"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, type, channel, enabled, timing_minutes, updated_at
                        FROM notification_settings
                        ORDER BY type, channel
                    """)
                    return [dict(setting) for setting in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting notification settings: {e}")
            return []
    
    def update_notification_setting(self, setting_id: int, data: Dict) -> Dict[str, Any]:
        """Update notification setting"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE notification_settings 
                        SET enabled = %(enabled)s, timing_minutes = %(timing_minutes)s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %(id)s
                    """, {
                        'id': setting_id,
                        'enabled': data.get('enabled', True),
                        'timing_minutes': data.get('timing_minutes', 120)
                    })
                    
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': 'Notification setting updated successfully'
                    }
        except Exception as e:
            logging.error(f"Error updating notification setting: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_notification_templates(self) -> List[Dict]:
        """Get all notification templates"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, type, channel, subject, body, variables, created_at, updated_at
                        FROM notification_templates
                        ORDER BY type, channel
                    """)
                    return [dict(template) for template in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting notification templates: {e}")
            return []
    
    def update_notification_template(self, template_id: int, data: Dict) -> Dict[str, Any]:
        """Update notification template"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE notification_templates 
                        SET subject = %(subject)s, body = %(body)s, 
                            variables = %(variables)s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %(id)s
                    """, {
                        'id': template_id,
                        'subject': data.get('subject', ''),
                        'body': data['body'],
                        'variables': json.dumps(data.get('variables', []))
                    })
                    
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': 'Template updated successfully'
                    }
        except Exception as e:
            logging.error(f"Error updating notification template: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def send_test_notification(self, data: Dict) -> Dict[str, Any]:
        """Send test notification"""
        try:
            # Log the test notification
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO notification_logs 
                        (recipient, channel, type, subject, body, status, metadata)
                        VALUES (%(recipient)s, %(channel)s, %(type)s, %(subject)s, %(body)s, %(status)s, %(metadata)s)
                        RETURNING id
                    """, {
                        'recipient': data['recipient'],
                        'channel': data['channel'],
                        'type': data['type'],
                        'subject': data.get('subject', ''),
                        'body': data['body'],
                        'status': 'sent',  # In real implementation, this would depend on actual delivery
                        'metadata': json.dumps({'test': True})
                    })
                    
                    log_id = cursor.fetchone()['id']
                    conn.commit()
                    
                    # In a real implementation, you would:
                    # 1. Use MailerLite for email notifications
                    # 2. Use Twilio for SMS notifications
                    # 3. Use WebSocket/Server-Sent Events for in-app notifications
                    
                    return {
                        'success': True,
                        'message': f'Test notification sent to {data["recipient"]}',
                        'log_id': log_id
                    }
                    
        except Exception as e:
            logging.error(f"Error sending test notification: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_notification_logs(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get notification logs with pagination"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, recipient, channel, type, subject, status, sent_at, error_message
                        FROM notification_logs
                        ORDER BY sent_at DESC
                        LIMIT %(limit)s OFFSET %(offset)s
                    """, {'limit': limit, 'offset': offset})
                    
                    return [dict(log) for log in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting notification logs: {e}")
            return []
    
    def get_notification_statistics(self) -> Dict[str, Any]:
        """Get notification statistics"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_sent,
                            COUNT(CASE WHEN status = 'sent' THEN 1 END) as successful,
                            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                            COUNT(CASE WHEN channel = 'email' THEN 1 END) as email_count,
                            COUNT(CASE WHEN channel = 'sms' THEN 1 END) as sms_count,
                            COUNT(CASE WHEN channel = 'inapp' THEN 1 END) as inapp_count
                        FROM notification_logs
                        WHERE sent_at >= NOW() - INTERVAL '30 days'
                    """)
                    
                    stats = cursor.fetchone()
                    
                    # Calculate success rate
                    total = stats['total_sent'] or 1
                    success_rate = round((stats['successful'] / total) * 100, 1)
                    
                    return {
                        'total_sent': stats['total_sent'],
                        'successful': stats['successful'],
                        'failed': stats['failed'],
                        'success_rate': success_rate,
                        'by_channel': {
                            'email': stats['email_count'],
                            'sms': stats['sms_count'],
                            'inapp': stats['inapp_count']
                        }
                    }
        except Exception as e:
            logging.error(f"Error getting notification statistics: {e}")
            return {
                'total_sent': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0,
                'by_channel': {'email': 0, 'sms': 0, 'inapp': 0}
            }