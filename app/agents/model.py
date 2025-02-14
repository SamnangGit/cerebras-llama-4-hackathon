from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
import base64
from agents.schemas.fuel_transaction import FuelTransactionBase


load_dotenv(override=True)

class GenerativeModel:
    def __init__(self, model_name: str, temperature: float = 0.5):
        self.model = ChatGoogleGenerativeAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model=model_name,
            temperature=temperature,
            verbose=True
        )

    def generate_text(self, prompt: str, image_path: str) -> str:
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_data}"
                    }
                ]
            )

            llm = self.model.with_structured_output(FuelTransactionBase)
            response = llm.invoke([message])
            return response

        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")

