# e:\lifetex\DHVB\ai_service.py
# import threading # No longer needed for local model initialization
# import google.generativeai as genai # No longer needed

# Local model imports (transformers) are no longer needed here as AIChatHandler
# now uses an external API.

class AIService:
    def __init__(self, app_instance):
        self.app = app_instance
        # Local AI model functionalities (generative pipeline, context building for local models)
        # have been removed as the application now relies on an external Bot API
        # handled by AIChatHandler.
        print("ℹ️ AIService initialized. Note: Local AI model functionalities have been removed.")
        # Any future generic, non-chat API interactions could be placed here if needed.
