"""Chat manager for Lumina AI application."""

import json
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime

class ChatManager:
    """Manages chat sessions and conversation history."""

    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize chat manager.

        Args:
            storage_dir: Optional path to storage directory.
        """
        if storage_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            storage_dir = os.path.join(base_dir, "conversations")

        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

        self.current_chat_id: Optional[str] = None
        self.current_chat_title: str = "Untitled Chat"
        self.history: List[Dict] = []
        self.conversations: List[Dict] = []
        self._load_conversations_index()

    def _load_conversations_index(self):
        """Build index of all conversations."""
        self.conversations = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.storage_dir, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.conversations.append({
                            "id": data.get("id"),
                            "title": data.get("title", "Untitled Chat"),
                            "updated_at": data.get("updated_at", 0)
                        })
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    
        self.conversations.sort(key=lambda x: x["updated_at"], reverse=True)

    def get_conversations(self) -> List[Dict]:
        """Get list of conversations.
        
        Returns:
            List of dicts with id, title, and updated_at.
        """
        return self.conversations

    def new_chat(self) -> str:
        """Start a new chat session.
        
        Returns:
            The ID of the new chat.
        """
        self.current_chat_id = str(uuid.uuid4())
        self.current_chat_title = "Untitled Chat"
        self.history = []
        self._save_current_chat(self.current_chat_title)
        self._load_conversations_index()
        return str(self.current_chat_id)

    def load_chat(self, chat_id: str) -> bool:
        """Load a specific chat session.
        
        Args:
            chat_id: ID of the chat to load.
            
        Returns:
            True if loaded successfully.
        """
        path = os.path.join(self.storage_dir, f"{chat_id}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_chat_id = data.get("id")
                    self.current_chat_title = data.get("title", "Untitled Chat")
                    self.history = data.get("history", [])
                return True
            except Exception:
                pass
        return False

    def add_message(self, role: str, content: str):
        """Add a message to the current chat memory."""
        self.history.append({"role": role, "content": content})
        self._save_current_chat()

    def _save_current_chat(self, title: Optional[str] = None):
        """Save the current chat session."""
        if not self.current_chat_id:
            return
            
        if title is not None:
            self.current_chat_title = title

        path = os.path.join(self.storage_dir, f"{self.current_chat_id}.json")
        
        data = {
            "id": self.current_chat_id,
            "title": self.current_chat_title,
            "updated_at": datetime.now().timestamp(),
            "history": self.history
        }
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self._update_index(str(self.current_chat_id), title, float(data.get("updated_at", 0.0)))
        except Exception as e:
            print(f"Error saving chat: {e}")

    def _update_index(self, chat_id: str, title: str, updated_at: float):
        """Update a conversation in the index."""
        found = False
        for c in self.conversations:
            if c["id"] == chat_id:
                c["title"] = title
                c["updated_at"] = updated_at
                found = True
                break
        if not found:
            self.conversations.append({
                "id": chat_id,
                "title": title,
                "updated_at": updated_at
            })
        self.conversations.sort(key=lambda x: x["updated_at"], reverse=True)

    def rename_chat(self, chat_id: str, new_title: str):
        """Rename a chat session."""
        if self.current_chat_id == chat_id:
            self.current_chat_title = new_title
            self._save_current_chat()
            return
            
        path = os.path.join(self.storage_dir, f"{chat_id}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["title"] = new_title
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self._update_index(chat_id, new_title, float(data.get("updated_at", 0.0)))
            except Exception as e:
                print(f"Error renaming chat: {e}")

    def delete_chat(self, chat_id: str):
        """Delete a chat session."""
        path = os.path.join(self.storage_dir, f"{chat_id}.json")
        if os.path.exists(path):
            os.remove(path)
        if self.current_chat_id == chat_id:
            self.current_chat_id = None
        self._load_conversations_index()
