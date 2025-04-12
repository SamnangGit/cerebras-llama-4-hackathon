from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cerebras import ChatCerebras
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
import base64

load_dotenv(override=True)

class GenerativeModel:
    def __init__(self):
        """Initialize GenerativeModel without immediate model creation"""
        pass

    def get_model(self, model_name: str, temperature: float = 0.5):
        """Create and return a ChatGoogleGenerativeAI instance"""
        return ChatGoogleGenerativeAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model=model_name,
            temperature=temperature,
            verbose=True
        )
    
    def get_cerebras_model(self, model_name: str, temperature: float = 0.5):
        return ChatCerebras(
            api_key=os.getenv("CEREBRAS_API_KEY"),
            model=model_name,
            tools=[],
            temperature=temperature,
            verbose=True
        )
