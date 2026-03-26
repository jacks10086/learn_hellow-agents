import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加载.env 文件中的环境变量
load_dotenv()

class HellowAgentsLLM:
    """
    为本书 "Hello Agents" 定制的LLM客户端。
    它用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
    """
    model: str = None      # 模型ID
    client: str = None     # 客户端实例
    
    def __init__(self, model:str =None, apiKey:str = None, baseUrl: str = None, timeout: int =None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        """

        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        # 所有不为空，否则抛出异常
        # 每个不为空，才返回True，空列表也是True
        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        # 初始化OpenAI客户端
        # 关键字参数，与位置无关，必须知道api_key、base_url、timeout在openAI文档的具体名称才行，可以与传统的位置参数混合使用
        #OpenAI构造函数调用, 只需传api_key和base_url即可
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)
    
    # 推理
    def think(self, messages:List[Dict[str, str]], temperature: float = 0)->str:
        """
        调用大语言模型进行思考，并返回其响应。
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                temperature =temperature,
                stream = True
            )

            # 处理流式响应
            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()  # 在流式输出结束后换行
            return "".join(collected_content)
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None

'''


'''
# --- 客户端使用示例 ---
if __name__ == '__main__':
    print("----客户端使用示例----")
    try:
        llmclient = HellowAgentsLLM()
        exampleMessages = [
            {"role": "system", "content": "你是一个专业的python程序员"},
            {"role": "user", "content": "写一个快速排序算法"}
        ]

        print("----调用LLM模型----")
        response = llmclient.think(exampleMessages)
        if response:
            print("\n\n----模型响应----")
            print(response)

    except Exception as e:
        print(f"❌ 调用LLM API时发生错误: {e}")