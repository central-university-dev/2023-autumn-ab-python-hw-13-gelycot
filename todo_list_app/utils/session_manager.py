import secrets
from datetime import timedelta, datetime


class SessionManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, user_id):
        token = secrets.token_hex(16)
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
        self.sessions[token] = {'user_id': user_id, 'exp': expiration_time}
        return token

    def get_user_id(self, token):
        session = self.sessions.get(token)
        if session and session['exp'] > datetime.utcnow():
            return session['user_id']
        return None

    def delete_session(self, token):
        if token in self.sessions:
            del self.sessions[token]


session_manager = SessionManager()