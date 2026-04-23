# Lumina AI

Lumina AI is a powerful, locally-hosted desktop chat application designed to interface with Ollama. It offers a sleek web-based UI built with TailwindCSS and PyQt6 WebEngine, prioritizing privacy and speed through on-device AI generation.

## Key Features
- **Local AI:** Connects to Ollama for privacy-focused, offline-capable AI chat.
- **Dynamic UI:** Beautiful, responsive frontend with dark and light themes, syntax highlighting, and an elegant conversational interface.
- **Local RAG:** Attach text and PDF files directly to your chats to provide dynamic context to the AI model.
- **Model Management:** Easily pull, delete, and switch between models natively within the application.
- **Conversation History:** Persists chat sessions locally with AI-generated titles and user renaming capabilities.
- **Custom Personas:** Configure custom system prompts and generation parameters (temperature, max tokens, top-p) for different personas.

## Installation
1. Ensure you have [Ollama](https://ollama.com/) installed and running locally.
2. Clone this repository:
   ```bash
   git clone https://github.com/RyanMaxiemus/lumina-ai.git
   cd lumina-ai
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python3 main.py
   ```

## License
This project is open-source and available under the MIT License.
