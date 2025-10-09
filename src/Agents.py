import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.runnables import ConfigurableField
from langchain_core.caches import InMemoryCache # 内存缓存，用于加速响应
from Storage import get_user
from Prompt import PromptClass
from Memory import MemoryClass
from Emotion import EmotionClass
from Tools import search,get_info_from_local,create_todo,checkSchedule,SetSchedule,SearchSchedule,ModifySchedule,DelSchedule,ConfirmDelSchedule

# 添加缓存以提高性能，避免重复请求相同内容时消耗额外的API调用
from langchain_core.globals import set_llm_cache
set_llm_cache(InMemoryCache())

load_dotenv(verbose= True, override= True)

class AgentClass:
    """
    AI 代理类，负责处理用户输入并生成回复
    整合了语言模型、记忆系统，情感分析和各种工具功能
    """
    def __init__(self):
        modelname = os.getenv("BASE_MODEL")
        backModel = os.getenv("BACK_MODEL")
        print(f"modelname= {modelname}, backModel={backModel }")
        # 设置备用模型，当主模型不可用的时候使用备用模型
        fallback_llm = ChatDeepSeek(
            model = modelname,
            api_key=os.getenv("DEEP_SEEK_API_KEY"),
            api_base=os.getenv("DEEP_SEEK_API_BASE"),
        )
        # 创建主聊天模型
        self.chatModel = ChatOpenAI(
            model=backModel,
            openai_api_key=os.getenv("SILLICONFLOW_API_KEY"),
            openai_api_base=os.getenv("SILLICONFLOW_API_BASE"),
        ).with_fallbacks([fallback_llm])

        # 设置可以用的工具列表，这些工具可以被AI代理调用
        self.tools = [search,get_info_from_local,create_todo,checkSchedule,SetSchedule,SearchSchedule,ModifySchedule,DelSchedule,ConfirmDelSchedule]

        # 从环境变量获取记忆键名
        self.memorykey = os.getenv("MEMORY_KEY")

        # 初始化情感状态，默认中性（5分）
        self.feeling = {"feeling": "default", "score": 5}

        # 创建提示词结构
        self.prompt = PromptClass(memorykey=self.memorykey, feeling=self.feeling).Prompt_Structure()

        # 初始化记忆系统
        self.memory = MemoryClass(memorykey=self.memorykey, model=modelname)

        # 初始化情感分析系统
        self.emotion = EmotionClass(model=modelname)

        # 创建agent
        self.agent = create_tool_calling_agent(
            self.chatModel,
            self.tools,
            self.prompt
        )

        # 创建代理执行器，整合代理，工具和记忆系统
        self.agent_chain = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory.set_memory(),
            verbose=True, # 启动详细输出，便于调试
        ).configurable_fields(
            # 设置可配置的记忆字段，允许在运行时修改记忆系统
            memory = ConfigurableField(
                id="agent_memory",
                name="Agent Memory",
                description="The Memory of the agent"
            )
        )

    def run_agent(self, input):
        """
        运行AI代理，处理用户输入
        :param input: 用户输入的文本
        :return: 包含AI回复的字典
        """
        print("\ninput-----------------》", input)
        # 进行情感分析，了解用户当前的情绪状态
        self.feeling = self.emotion.Emotion_Sensing(input)

        # 根据用户的的情绪状态，更新提示词结构
        self.prompt = PromptClass(memorykey=self.memorykey, feeling=self.feeling).Prompt_Structure()
        print("self.prompt", self.prompt)

        # 运行代理链，处理用户输入
        # 根据当前用户ID设置对于的记忆
        res = self.agent_chain.with_config({
            "agent_memory": self.memory.set_memory(session_id=get_user("userid"))
        }).invoke(
            {"input": input} # 传入用户输入
        )
        return res # 返回代理处理结果

