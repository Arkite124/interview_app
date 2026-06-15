from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

def get_model():
    """provider prefix가 포함된 ChatModel을 돌려준다"""
    return init_chat_model("openai:gpt-5.4-nano") # 프로바이더 표기

print(get_model())

# 프리픽스가 없으면 (prefix -> "openai":gpt-5.4-nano)
if __name__=="__main__":
    model=get_model()
    response=model.invoke("LangChain을 한 문장으로 설명 해 줘")
    print(type(response),response.content)
    