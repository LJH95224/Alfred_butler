import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import requests
import json

load_dotenv(verbose=True, override=True)

# llm = ChatOpenAI(
#     temperature=0,
#     model=os.getenv('BACK_MODEL'),
#     openai_api_key=os.getenv("SILLICONFLOW_API_KEY"),
#     openai_api_base=os.getenv("SILLICONFLOW_API_BASE"),
# )
# response = llm.invoke("Hello, world!")
# print(response)

def get_access_token() -> str:
    app_key = os.getenv("CLIENT_ID")
    app_secret = os.getenv("CLIENT_SECRET")

    try:
        response = requests.post(
            "https://api.dingtalk.com/v1.0/oauth2/accessToken",
            json={"appKey": app_key, "appSecret": app_secret}
        )
        response.raise_for_status()
        data = json.loads(response.text)
        token = data.get("accessToken")
        if not token:
            raise ValueError("获取钉钉访问令牌失败")
        return token
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"获取访问令牌失败: {str(e)}")


token = get_access_token()
print(token)