from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()

import os
from serpapi import SerpApiClient
from typing import Callable, Dict, Any

def search(query: str) -> str:
    """
    一个基于SerpApi的实战网页搜索引擎工具。
    """
    print(f"[SerpApi] 正在执行网页搜索: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：SERPAPI_API_KEY 未在 .env 文件中配置。"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",  # 国家代码
            "hl": "zh-cn", # 语言代码
        }
        
        client = SerpApiClient(params)
        results = client.get_dict()
        
        # 智能解析：优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        
        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"   



class ToolExecutor:
    """
    为本书 "Hello Agents" 定制的工具箱。
    它用于存储和管理所有可用的工具。
    """
    # 工具字典，键为工具名称，值为工具信息（包括描述和函数）
    tools: Dict[str,Dict[str, Any]] = {}

    def __init__(self):
        self.tools = {}
    # 注册工具, name:工具名称, description:工具描述, func:工具函数
    def registerTool(self, name:str, description: str, func:Callable):
        if name in self.tools:
            print(f"警告:工具 {name} 已注册，将被覆盖。")

        self.tools[name] = {"description": description, "func": func}
        print(f"工具 {name} 已注册")
        
    # 获取工具函数, name:工具名称
    # 返回:工具函数（如果已注册），否则返回None
    def getTool(self, name:str)->Callable:
        if name in self.tools:
            return self.tools[name]["func"]
        else:
            print(f"错误:未注册工具: {name}。")
            return None
    
    def getAvailableTools(self)->str:
        return "\n".join([
            f"{key}: {value['description']}"
            for key, value in self.tools.items()
        ])


if __name__ == '__main__':
    print("Hello AgentsTools 工具箱测试")
    # 1. 初始化工具执行器
    toolExecutor = ToolExecutor()

    # 2. 注册我们的实战搜索工具
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search", search_description, search)
    
    # 3. 打印可用的工具
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())

    # 4. 智能体的Action调用，这次我们问一个实时性的问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误：未找到名为 '{tool_name}' 的工具。")