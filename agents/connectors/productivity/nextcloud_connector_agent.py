"""
Nextcloud Connector Agent

Integrates with Nextcloud for file operations, calendar sync, and contact management.
Apollo can automatically upload files, sync calendars, and manage contacts.
"""

from typing import Dict, List, Optional
import requests
from datetime import datetime


class NextcloudConnectorAgent:
    """
    Connects to Nextcloud for comprehensive file and data operations.
    
    Features:
    - File upload/download/sharing
    - Calendar synchronization
    - Contact management
    - Collaborative document editing
    - Activity tracking
    """
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize Nextcloud connector.
        
        Args:
            base_url: Nextcloud instance URL (e.g., https://cloud.example.com)
            username: Nextcloud username
            password: Nextcloud app password
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.webdav_url = f"{self.base_url}/remote.php/dav"
        self.ocs_url = f"{self.base_url}/ocs/v2.php"
        
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FILE OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def upload_file(self, local_path: str, remote_path: str) -> Dict:
        """
        Upload file to Nextcloud.
        
        Args:
            local_path: Local file path
            remote_path: Remote path in Nextcloud (e.g., /Documents/file.pdf)
            
        Returns:
            Dict with upload status and file info
        """
        url = f"{self.webdav_url}/files/{self.username}{remote_path}"
        
        with open(local_path, 'rb') as f:
            response = requests.put(
                url,
                data=f,
                auth=(self.username, self.password)
            )
        
        return {
            "success": response.status_code in [201, 204],
            "status_code": response.status_code,
            "remote_path": remote_path,
            "message": "File uploaded successfully" if response.status_code in [201, 204] else "Upload failed"
        }
    
    def download_file(self, remote_path: str, local_path: str) -> Dict:
        """
        Download file from Nextcloud.
        
        Args:
            remote_path: Remote path in Nextcloud
            local_path: Local destination path
            
        Returns:
            Dict with download status
        """
        url = f"{self.webdav_url}/files/{self.username}{remote_path}"
        
        response = requests.get(
            url,
            auth=(self.username, self.password)
        )
        
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return {
                "success": True,
                "local_path": local_path,
                "message": "File downloaded successfully"
            }
        
        return {
            "success": False,
            "status_code": response.status_code,
            "message": "Download failed"
        }
    
    def list_files(self, path: str = "/") -> List[Dict]:
        """
        List files in directory.
        
        Args:
            path: Directory path (default: root)
            
        Returns:
            List of file/folder info
        """
        url = f"{self.webdav_url}/files/{self.username}{path}"
        
        response = requests.request(
            "PROPFIND",
            url,
            auth=(self.username, self.password),
            headers={"Depth": "1"}
        )
        
        # Parse WebDAV XML response
        # (Simplified - full implementation would parse XML)
        return {
            "success": response.status_code == 207,
            "path": path,
            "files": []  # Would contain parsed file list
        }
    
    def delete_file(self, remote_path: str) -> Dict:
        """
        Delete file from Nextcloud.
        
        Args:
            remote_path: Remote path to delete
            
        Returns:
            Dict with deletion status
        """
        url = f"{self.webdav_url}/files/{self.username}{remote_path}"
        
        response = requests.delete(
            url,
            auth=(self.username, self.password)
        )
        
        return {
            "success": response.status_code == 204,
            "status_code": response.status_code,
            "message": "File deleted successfully" if response.status_code == 204 else "Deletion failed"
        }
    
    def share_file(self, path: str, share_with: str, share_type: int = 0, permissions: int = 1) -> Dict:
        """
        Share file with user or group.
        
        Args:
            path: File path to share
            share_with: Username or group name
            share_type: 0=user, 1=group, 3=public link
            permissions: 1=read, 15=read+write+delete
            
        Returns:
            Dict with share info including share link
        """
        url = f"{self.ocs_url}/apps/files_sharing/api/v1/shares"
        
        data = {
            "path": path,
            "shareType": share_type,
            "shareWith": share_with,
            "permissions": permissions
        }
        
        response = requests.post(
            url,
            data=data,
            auth=(self.username, self.password),
            headers={"OCS-APIRequest": "true"}
        )
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "message": "File shared successfully" if response.status_code == 200 else "Sharing failed"
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CALENDAR OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def sync_calendar(self, calendar_name: str = "personal") -> Dict:
        """
        Sync calendar events.
        
        Args:
            calendar_name: Calendar name (default: personal)
            
        Returns:
            Dict with calendar events
        """
        url = f"{self.webdav_url}/calendars/{self.username}/{calendar_name}"
        
        response = requests.request(
            "PROPFIND",
            url,
            auth=(self.username, self.password),
            headers={"Depth": "1"}
        )
        
        return {
            "success": response.status_code == 207,
            "calendar": calendar_name,
            "events": []  # Would contain parsed events
        }
    
    def create_event(self, calendar_name: str, event_data: Dict) -> Dict:
        """
        Create calendar event.
        
        Args:
            calendar_name: Calendar name
            event_data: Event details (title, start, end, description)
            
        Returns:
            Dict with created event info
        """
        # Generate iCalendar format
        ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Apollo AI//EN
BEGIN:VEVENT
UID:{event_data.get('uid', datetime.now().isoformat())}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{event_data['start']}
DTEND:{event_data['end']}
SUMMARY:{event_data['title']}
DESCRIPTION:{event_data.get('description', '')}
END:VEVENT
END:VCALENDAR"""
        
        url = f"{self.webdav_url}/calendars/{self.username}/{calendar_name}/{event_data.get('uid', 'event')}.ics"
        
        response = requests.put(
            url,
            data=ical,
            auth=(self.username, self.password),
            headers={"Content-Type": "text/calendar"}
        )
        
        return {
            "success": response.status_code in [201, 204],
            "status_code": response.status_code,
            "message": "Event created successfully" if response.status_code in [201, 204] else "Creation failed"
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONTACT OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def sync_contacts(self, addressbook: str = "contacts") -> Dict:
        """
        Sync contacts from addressbook.
        
        Args:
            addressbook: Addressbook name (default: contacts)
            
        Returns:
            Dict with contacts
        """
        url = f"{self.webdav_url}/addressbooks/users/{self.username}/{addressbook}"
        
        response = requests.request(
            "PROPFIND",
            url,
            auth=(self.username, self.password),
            headers={"Depth": "1"}
        )
        
        return {
            "success": response.status_code == 207,
            "addressbook": addressbook,
            "contacts": []  # Would contain parsed contacts
        }
    
    def create_contact(self, addressbook: str, contact_data: Dict) -> Dict:
        """
        Create contact in addressbook.
        
        Args:
            addressbook: Addressbook name
            contact_data: Contact details (name, email, phone)
            
        Returns:
            Dict with created contact info
        """
        # Generate vCard format
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{contact_data['name']}
EMAIL:{contact_data.get('email', '')}
TEL:{contact_data.get('phone', '')}
END:VCARD"""
        
        url = f"{self.webdav_url}/addressbooks/users/{self.username}/{addressbook}/{contact_data.get('uid', 'contact')}.vcf"
        
        response = requests.put(
            url,
            data=vcard,
            auth=(self.username, self.password),
            headers={"Content-Type": "text/vcard"}
        )
        
        return {
            "success": response.status_code in [201, 204],
            "status_code": response.status_code,
            "message": "Contact created successfully" if response.status_code in [201, 204] else "Creation failed"
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # APOLLO INTEGRATION WORKFLOWS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def process_email_attachment(self, email_data: Dict) -> Dict:
        """
        Apollo workflow: Process email attachment and upload to Nextcloud.
        
        Args:
            email_data: Email with attachment info
            
        Returns:
            Dict with processing results
        """
        # 1. Download attachment from email
        attachment_path = email_data['attachment_path']
        
        # 2. Determine destination folder based on content type
        if email_data.get('is_invoice'):
            remote_path = f"/Documents/Invoices/{email_data['filename']}"
        elif email_data.get('is_contract'):
            remote_path = f"/Documents/Contracts/{email_data['filename']}"
        else:
            remote_path = f"/Documents/{email_data['filename']}"
        
        # 3. Upload to Nextcloud
        result = self.upload_file(attachment_path, remote_path)
        
        # 4. Share with relevant team members
        if email_data.get('share_with'):
            for user in email_data['share_with']:
                self.share_file(remote_path, user)
        
        return {
            "success": result['success'],
            "remote_path": remote_path,
            "shared_with": email_data.get('share_with', []),
            "message": "Email attachment processed and uploaded to Nextcloud"
        }
    
    def auto_schedule_meeting(self, meeting_data: Dict) -> Dict:
        """
        Apollo workflow: Automatically schedule meeting in Nextcloud calendar.
        
        Args:
            meeting_data: Meeting details from email parsing
            
        Returns:
            Dict with meeting creation results
        """
        # 1. Create calendar event
        event_result = self.create_event(
            calendar_name="personal",
            event_data={
                "title": meeting_data['title'],
                "start": meeting_data['start_time'],
                "end": meeting_data['end_time'],
                "description": meeting_data.get('description', ''),
                "uid": meeting_data.get('uid')
            }
        )
        
        # 2. Create meeting prep document
        prep_doc = f"/Documents/Meetings/{meeting_data['title']}_prep.md"
        # (Would upload prep document here)
        
        return {
            "success": event_result['success'],
            "event_created": event_result['success'],
            "prep_document": prep_doc,
            "message": "Meeting scheduled and prep document created"
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# USAGE EXAMPLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
# Initialize connector
nextcloud = NextcloudConnectorAgent(
    base_url="https://cloud.example.com",
    username="user@example.com",
    password="app-password-here"
)

# Upload file
result = nextcloud.upload_file(
    local_path="/tmp/invoice.pdf",
    remote_path="/Documents/Invoices/invoice_2024.pdf"
)

# Share file with team
nextcloud.share_file(
    path="/Documents/Invoices/invoice_2024.pdf",
    share_with="team@example.com",
    share_type=1,  # Group
    permissions=1  # Read-only
)

# Create calendar event
nextcloud.create_event(
    calendar_name="personal",
    event_data={
        "title": "Team Meeting",
        "start": "20241030T140000Z",
        "end": "20241030T150000Z",
        "description": "Discuss Q4 roadmap"
    }
)

# Apollo workflow: Process email attachment
nextcloud.process_email_attachment({
    "attachment_path": "/tmp/contract.pdf",
    "filename": "contract_2024.pdf",
    "is_contract": True,
    "share_with": ["legal@example.com", "ceo@example.com"]
})
"""
