#TODO: Extend to a unstructured to persist conversation data and add retention policy
class ConversationManager:
    def __init__(self):
        self.conversations = {}

    def add_message(self, session_id: str, message: dict):
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append(message)

    def get_history(self, session_id: str = "default"):
        return self.conversations.get(session_id, [])

    def clear_history(self, session_id: str = "default"):
        if session_id in self.conversations:
            self.conversations[session_id].clear()
