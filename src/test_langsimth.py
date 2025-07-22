import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    temperature=0,
    model="deepseek-chat",
    openai_api_key=os.environ["DEEP_SEEK_API_KEY"],
    openai_api_base=os.environ["DEEP_SEEK_API_BASE"],
)
response = llm.invoke("Hello, world!")
print(response)