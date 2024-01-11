import os
from openai import OpenAI 
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)