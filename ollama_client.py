"""Ollama client for Lumina AI application."""

import json
import queue
import requests
import threading
from typing import Callable, Dict, List, Optional, Generator


class OllamaError(Exception):
    """Base exception for Ollama client errors."""
    pass


class ConnectionError(OllamaError):
    """Raised when cannot connect to Ollama server."""
    pass


class ModelError(OllamaError):
    """Raised when model is not found or invalid."""
    pass


class APIError(OllamaError):
    """Raised when API returns an error."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama client.

        Args:
            base_url: Base URL for Ollama API.
        """
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        """Set base URL."""
        self._base_url = value.rstrip("/")

    def _check_connection(self) -> bool:
        """Check if Ollama server is reachable.

        Returns:
            True if connection is successful.
        """
        try:
            response = self._session.get(f"{self._base_url}/", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_models(self) -> List[Dict[str, str]]:
        """Get list of available models.

        Returns:
            List of model info dictionaries with 'name' and other metadata.

        Raises:
            ConnectionError: If cannot connect to server.
            APIError: If API returns an error.
        """
        try:
            response = self._session.get(
                f"{self._base_url}/api/tags",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            elif response.status_code == 404:
                # Older Ollama versions
                return []
            else:
                raise APIError(
                    f"Failed to get models: {response.text}",
                    response.status_code
                )

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot connect to Ollama at {self._base_url}. Is Ollama running?")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.9,
        stream: bool = True,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Generate a response from the model.

        Args:
            model: Model name to use.
            prompt: User prompt.
            system: Optional system prompt.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.
            top_p: Nucleus sampling parameter (0.0 to 1.0).
            stream: Whether to stream the response.
            callback: Optional callback function for streaming responses.

        Returns:
            Full generated response text.

        Raises:
            ConnectionError: If cannot connect to server.
            ModelError: If model is not found.
            APIError: If API returns an error.
        """
        url = f"{self._base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": top_p,
            }
        }

        if system:
            payload["system"] = system

        try:
            if stream and callback:
                return self._stream_generate(url, payload, callback)
            else:
                return self._generate_non_stream(url, payload)

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot connect to Ollama at {self._base_url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise APIError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.9,
        stream: bool = True,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Generate a response using the chat API.

        Args:
            model: Model name to use.
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.
            top_p: Nucleus sampling parameter (0.0 to 1.0).
            stream: Whether to stream the response.
            callback: Optional callback function for streaming responses.

        Returns:
            Full generated response text.

        Raises:
            ConnectionError: If cannot connect to server.
            ModelError: If model is not found.
            APIError: If API returns an error.
        """
        url = f"{self._base_url}/api/chat"

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": top_p,
            }
        }

        try:
            if stream and callback:
                return self._stream_chat(url, payload, callback)
            else:
                return self._chat_non_stream(url, payload)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Fallback to /api/generate for older Ollama versions
                return self._chat_fallback(model, messages, temperature, max_tokens, top_p, stream, callback)
            raise APIError(f"Request failed: {str(e)}", e.response.status_code)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot connect to Ollama at {self._base_url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise APIError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def _chat_fallback(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.9,
        stream: bool = True,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Fallback to /api/generate for older Ollama versions."""
        # Convert messages to a simple prompt
        prompt_parts = []
        system_msg = None
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_msg = content
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
        
        return self.generate(
            model=model,
            prompt=prompt,
            system=system_msg,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=stream,
            callback=callback,
        )

    def _stream_chat(
        self,
        url: str,
        payload: Dict,
        callback: Callable[[str], None]
    ) -> str:
        """Handle streaming chat response."""
        response = self._session.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        full_response = []

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        token = data["message"]["content"]
                        if token:  # Skip empty tokens
                            full_response.append(token)
                            callback(token)

                    if data.get("done", False):
                        break

                except json.JSONDecodeError:
                    continue

        return "".join(full_response)

    def _chat_non_stream(self, url: str, payload: Dict) -> str:
        """Handle non-streaming chat response."""
        payload["stream"] = False

        response = self._session.post(url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        if "message" in data:
            return data["message"].get("content", "")
        return ""

    def _stream_generate(
        self,
        url: str,
        payload: Dict,
        callback: Callable[[str], None]
    ) -> str:
        """Handle streaming generation.

        Args:
            url: API URL.
            payload: Request payload.
            callback: Callback for each token.

        Returns:
            Full response text.
        """
        response = self._session.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        full_response = []

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        token = data["response"]
                        full_response.append(token)
                        callback(token)

                    # Check for done
                    if data.get("done", False):
                        break

                except json.JSONDecodeError:
                    continue

        return "".join(full_response)

    def _generate_non_stream(self, url: str, payload: Dict) -> str:
        """Handle non-streaming generation.

        Args:
            url: API URL.
            payload: Request payload.

        Returns:
            Response text.
        """
        payload["stream"] = False

        response = self._session.post(url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Ollama server.

        Returns:
            Tuple of (success, message).
        """
        try:
            if not self._check_connection():
                return False, f"Cannot connect to {self._base_url}. Is Ollama running?"

            # Try to get models to verify API works
            self.get_models()
            return True, "Connected"

        except ConnectionError as e:
            return False, str(e)
        except APIError as e:
            return False, f"API Error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def pull_model(
        self,
        name: str,
        stream: bool = True,
        callback: Optional[Callable[[Dict], None]] = None,
    ) -> bool:
        """Pull a model from the registry."""
        url = f"{self._base_url}/api/pull"
        payload = {"name": name, "stream": stream}
        
        try:
            if stream and callback:
                response = self._session.post(url, json=payload, stream=True, timeout=120)
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        try:
                            callback(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                return True
            else:
                response = self._session.post(url, json=payload, timeout=120)
                response.raise_for_status()
                return True
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to pull model: {str(e)}")

    def delete_model(self, name: str) -> bool:
        """Delete a local model."""
        url = f"{self._base_url}/api/delete"
        payload = {"name": name}
        try:
            response = self._session.request("DELETE", url, json=payload, timeout=30)
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                raise APIError(f"Failed to delete model: {response.text}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")



