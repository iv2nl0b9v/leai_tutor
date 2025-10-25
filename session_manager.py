"""
Session management and storage functionality
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import asdict
from datetime import datetime

from models import Session


def save_session(session: Session, sessions_dir: Path) -> str:
    """Save a session to JSON file"""
    if not session.session_id:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session.session_id = f"session_{timestamp}"
    
    filepath = sessions_dir / f"{session.session_id}.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(asdict(session), f, indent=2, ensure_ascii=False)
    
    return session.session_id


def load_session(session_id: str, sessions_dir: Path) -> Optional[Session]:
    """Load a session from JSON file"""
    filepath = sessions_dir / f"{session_id}.json"
    
    if not filepath.exists():
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Session(**data)
    except Exception as e:
        print(f"Error loading session {session_id}: {e}")
        return None


def list_sessions(sessions_dir: Path) -> List[Dict]:
    """List all available sessions"""
    sessions = []
    
    for json_file in sessions_dir.glob("session_*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            sessions.append({
                'session_id': data['session_id'],
                'topic_name': data['topic_name'],
                'created_at': data['created_at'],
                'status': data.get('status', 'active'),
                'message_count': len(data.get('messages', []))
            })
        except Exception as e:
            print(f"Error reading session {json_file}: {e}")
    
    # Sort by created_at, newest first
    sessions.sort(key=lambda x: x['created_at'], reverse=True)
    return sessions

