import time
import threading
import random
import string


class SessionStore:
    def __init__(self):
        self._sessions = {}
        self._lock = threading.Lock()

    def create_session(self, data: dict, expiry_time_seconds: int = 600) -> str:
        session_id = self._generate_session_id()
        expiry_time = time.time() + expiry_time_seconds
        with self._lock:
            self._sessions[session_id] = {
                "data": data,
                "expiry_time": expiry_time,
            }
            return session_id

    def retrieve_session_data(self, session_id: str) -> str:
        with self._lock:
            session_info = self._sessions.get(session_id)
            if session_info and session_info["expiry_time"] > time.time():
                return session_info
            else:
                self._cleanup_session(session_id)
                return None

    def end_session(self, session_id: str) -> None:
        with self._lock:
            self._cleanup_session(session_id)

    def _cleanup_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._sessions.pop(session_id)

    def _generate_session_id(self, length: int = 20) -> str:
        characters = string.ascii_letters + string.digits
        session_id = "".join(random.choice(characters) for _ in range(length))
        while session_id in self._sessions:  # Ensure session ID is unique
            session_id = "".join(random.choice(characters) for _ in range(length))
        return session_id


if __name__ == "__main__":
    store = SessionStore()
    session_id = store.create_session(
        "1234567890"
    )  # Store OTP valid for 600 seconds (10 minutes)
    print("Created session:", session_id)

    stored_data = store.retrieve_session_data(session_id)
    print("Retrieved data:", stored_data)

    time.sleep(5)  # Simulate passage of time (5 seconds)

    stored_data = store.retrieve_session_data(session_id)
    print("Retrieved data after 5 seconds:", stored_data)

    store.end_session(session_id)
    print("Session ended.")

    stored_data = store.retrieve_session_data(session_id)
    print("Retrieved data after ending session:", stored_data)
