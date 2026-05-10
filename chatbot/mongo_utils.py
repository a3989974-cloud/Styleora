import os
import json
from datetime import datetime, timezone
from urllib.parse import urlparse

MONGO_URI = os.environ.get('MONGODB_URI', '')
MONGO_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'styleora_chatbot')

_client = None
_db = None


def get_db():
    global _client, _db
    if _db is not None:
        return _db
    if not MONGO_URI:
        _db = None
        return _db
    try:
        import pymongo
        _client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
        _client.admin.command('ping')
        _db = _client[MONGO_DB_NAME]
        _db.sessions.create_index('session_id', unique=True)
        _db.sessions.create_index('updated_at')
        _db.messages.create_index('session_id')
        _db.messages.create_index('timestamp')
    except Exception:
        _db = None
    return _db


def is_connected():
    db = get_db()
    return db is not None


def create_session(session_id):
    db = get_db()
    if db is None:
        return None
    now = datetime.now(timezone.utc)
    db.sessions.update_one(
        {'session_id': session_id},
        {'$set': {'session_id': session_id, 'updated_at': now, 'created_at': now}},
        upsert=True
    )
    return session_id


def save_message(session_id, role, content):
    db = get_db()
    if db is None:
        return None
    now = datetime.now(timezone.utc)
    msg = {
        'session_id': session_id,
        'role': role,
        'content': content,
        'timestamp': now,
    }
    db.messages.insert_one(msg)
    db.sessions.update_one(
        {'session_id': session_id},
        {'$set': {'updated_at': now}}
    )
    return msg


def get_history(session_id, limit=50):
    db = get_db()
    if db is None:
        return []
    cursor = db.messages.find(
        {'session_id': session_id},
        {'_id': 0, 'session_id': 0}
    ).sort('timestamp', 1).limit(limit)
    return list(cursor)


def clear_history(session_id):
    db = get_db()
    if db is None:
        return False
    db.messages.delete_many({'session_id': session_id})
    db.sessions.delete_one({'session_id': session_id})
    return True


def get_all_sessions(limit=50):
    db = get_db()
    if db is None:
        return []
    cursor = db.sessions.find(
        {},
        {'_id': 0}
    ).sort('updated_at', -1).limit(limit)
    return list(cursor)


def get_session_message_count(session_id):
    db = get_db()
    if db is None:
        return 0
    return db.messages.count_documents({'session_id': session_id})
