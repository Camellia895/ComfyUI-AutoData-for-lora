# Last updated: 2025-05-21 23:05:40

import os
import subprocess
import sys
import json
import re
import traceback # 用于打印更详细的错误信息

# --- ComfyUI 服务器实例 ---
# 我们需要这个来注册API端点
# 这通常在 ComfyUI 的 server.py 中定义并作为全局变量 server.PromptServer.instance 存在
# 为了在节点文件中引用它，我们可能需要稍微变通一下，或者假设它在加载时可用。
# 一个更安全的方式是在 __init__.py 中获取并传递它，或者在节点加载时从 server 获取。
# 这里我们先尝试直接引用，如果不行再调整。
try:
    import server # 尝试导入 ComfyUI 的 server 模块
    PromptServer = server.PromptServer
except ImportError:
    # 如果直接导入失败 (例如在某些测试环境中)，可以尝试从已加载的模块中查找
    # 或者在 ComfyUI 启动后，这个实例应该是可用的
    if hasattr(sys.modules.get("server", None), "PromptServer"):
        PromptServer = sys.modules["server"].PromptServer
    else:
        # 如果还是找不到，提供一个占位符，API功能将不可用
        class MockPromptServer:
            def __init__(self):
                self.instance = self
                self.routes = self # 模拟 Flask app 的 routes
            def add_routes(self, func, path, methods=None): # 模拟 add_url_rule
                print(f"警告: PromptServer 未正确加载，API端点 '{path}' 将无法注册。")
            def get(self, path): # 模拟 @routes.get
                def decorator(func):
                    self.add_routes(func, path, methods=['GET'])
                    return func
                return decorator
        PromptServer = MockPromptServer()
        print("警告: 未能加载 ComfyUI PromptServer。API端点功能将受限。")

try:
    from aiohttp import web
except ImportError:
    print("错误: 无法导入 aiohttp.web。请确保 aiohttp 已安装在 ComfyUI 的 Python 环境中。")
    # 定义一个假的 web.json_response 以免后续代码完全崩溃，但API会失效
    class MockWeb:
        @staticmethod
        def json_response(data, status=200, reason=None, headers=None):
            print(f"警告: aiohttp.web 未加载，无法发送真实JSON响应。Data: {data}, Status: {status}")
            # 实际应用中，这里应该返回一个能被 aiohttp 处理的 Response 对象
            # 但作为 Mock，我们可能什么都不做或抛异常，或者返回一个简单的文本响应
            # 为了让代码不直接崩溃，我们可以返回一个模拟的 Response 对象，尽管它可能不完全兼容
            class MockResponse:
                def __init__(self, text, status, reason, headers):
                    self.text = text
                    self.status = status
                    self.reason = reason
                    self.headers = headers if headers else {}
            return MockResponse(json.dumps(data), status, reason, headers) # 返回模拟对象
    web = MockWeb()

# --- 配置 ---
NODE_FILE_DIR = os.path.dirname(os.path.abspath(__file__)) # 当前 .py 文件所在的目录
PORTABLE_SCRIPTS_SUBDIR = "portable_scripts"
PORTABLE_SCRIPTS_PATH = os.path.join(NODE_FILE_DIR, PORTABLE_SCRIPTS_SUBDIR)

# --- 辅助函数：从脚本文件内容中提取JSON元数据 ---
def extract_json_from_script_content(content):
    match = re.search(r"#\s*COMFY_NODE_PARAMS_JSON_START\s*#\s*({.*?})\s*#\s*COMFY_NODE_PARAMS_JSON_END", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            print(f"错误: 解析脚本中的JSON元数据失败: {e}")
    return None

# --- 辅助函数：获取脚本列表（仅文件名）---
def get_script_filenames():
    if not os.path.exists(PORTABLE_SCRIPTS_PATH):
        os.makedirs(PORTABLE_SCRIPTS_PATH, exist_ok=True)
        return ["未找到脚本"]
    scripts = [f for f in os.listdir(PORTABLE_SCRIPTS_PATH) if f.endswith(".py") and os.path.isfile(os.path.join(PORTABLE_SCRIPTS_PATH, f))]
    return sorted(scripts) if scripts else ["未找到脚本"]


class 便携脚本执行器_动态JS:
    NAME = "便携脚本执行器 (JS动态接口)" # 用于JS引用的内部名称
    CATEGORY = "实用工具/脚本 (JS)"

    # 初始的、最少的Python端输入
    # JS 将会根据选择的脚本动态添加UI元素，并将值通过 "dynamic_params_json" 回传
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "选择脚本": (get_script_filenames(), ),
                "目标文件夹": ("STRING", {"default": "D:/示例/目标文件夹"}), # 确保所有必需的都在这里
                "触发器": ("*",),
                "prompt": "PROMPT",             # 将 prompt 和 extra_pnginfo 移到 required 或 hidden
                "extra_pnginfo": "EXTRA_PNGINFO", # 通常它们是必需的或由系统在隐藏模式下提供
            },
            "optional": { # <--- 创建或使用 "optional" 字典块
                "dynamic_params_json": ("STRING", {"default": "{}"}), # <--- 将 dynamic_params_json 移到这里
            },
            "hidden": { # <--- "hidden" 字典块现在可能只剩下 prompt 和 extra_pnginfo，或者根据您的设计调整
                # 如果 prompt 和 extra_pnginfo 移到了 required，这里就可以是空的，或者完全移除 "hidden" 键
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("状态报告",)
    FUNCTION = "执行脚本_接收动态参数"

    # Python端的执行函数
    def 执行脚本_接收动态参数(self, 选择脚本, 目标文件夹, 触发器, dynamic_params_json, prompt=None, extra_pnginfo=None):
        if 选择脚本 == "未找到脚本":
            return ("错误：未选择脚本。",)

        脚本完整路径 = os.path.join(PORTABLE_SCRIPTS_PATH, 选择脚本)
        if not os.path.isfile(脚本完整路径):
            return (f"错误：脚本 '{选择脚本}' 未找到。",)
        if not os.path.isdir(目标文件夹):
            return (f"错误：目标文件夹 '{目标文件夹}' 不存在。",)

        要使用的解释器 = sys.executable # 使用当前ComfyUI的Python解释器
        命令 = [要使用的解释器, 脚本完整路径, "--target_folder", 目标文件夹]

        # 解析从JS传来的动态参数JSON
        try:
            dynamic_params = json.loads(dynamic_params_json)
        except json.JSONDecodeError:
            dynamic_params = {}
            print(f"警告: 动态参数JSON解析失败: '{dynamic_params_json}'")

        # 将动态参数添加到命令中 (假设它们对应脚本的命令行参数)
        # 注意：这里假设 dynamic_params 的键是脚本期望的命令行参数名 (如 "text_input")
        # 并且脚本的 argparse 定义了 --text_input 这样的参数
        for param_name, param_value in dynamic_params.items():
            # 对于布尔参数，如果为True，通常只添加参数名，否则不添加
            # 这里需要根据参数元数据中的 'type' 来判断
            # 为了简单起见，我们先假设JS会正确处理布尔值的传递
            # （例如，如果脚本期望 --verbose，JS如果checkbox选中，dynamic_params["verbose"]=True)
            # 外部脚本的 argparse 需要能处理这种情况 (如 action="store_true")
            # 或者，JS传递的布尔值也可能是 "true"/"false" 字符串

            # 简化的处理：
            if isinstance(param_value, bool):
                if param_value: # 如果是 True，添加参数名 (例如 --verbose)
                    命令.append(f"--{param_name}")
            else: # 其他类型，添加参数名和值
                命令.append(f"--{param_name}")
                命令.append(str(param_value))

        状态消息 = f"准备执行: {' '.join(命令)}\n"
        print(状态消息)

        try:
            进程 = subprocess.run(命令, capture_output=True, text=True, check=False, encoding='utf-8', errors='replace', cwd=NODE_FILE_DIR)
            if 进程.stdout: 状态消息 += f"脚本STDOUT:\n{进程.stdout}\n"
            if 进程.stderr: 状态消息 += f"脚本STDERR:\n{进程.stderr}\n"
            状态消息 += f"脚本 '{选择脚本}' 执行完毕，返回码: {进程.returncode}。"
        except Exception as e:
            状态消息 = f"运行脚本时发生意外错误: {str(e)}\n{traceback.format_exc()}"

        return (状态消息,)

# --- API 端点：获取脚本参数定义 ---
# 需要在 ComfyUI 服务器启动时注册这个路由
# 这个装饰器通常用在 server.py 中，或者节点类可以有特殊方法来注册
# 我们尝试使用 PromptServer.instance (如果可用)
# 注意：路由路径需要是唯一的
@PromptServer.instance.routes.get("/comfy_portable_script_executor/get_script_params")
async def get_script_params_endpoint(request): # request 参数是 aiohttp 传递的
    """
    API端点，根据请求的脚本名返回其参数定义的JSON。
    """
    script_name_param = request.rel_url.query.get('script_name')
    if not script_name_param:
        # 使用 aiohttp.web.json_response
        return web.json_response({"error": "缺少 script_name 参数"}, status=400)

    script_path = os.path.join(PORTABLE_SCRIPTS_PATH, script_name_param) # 确保 PORTABLE_SCRIPTS_PATH 定义正确
    
    if not os.path.isfile(script_path):
        return web.json_response({"error": f"脚本 '{script_name_param}' 未找到"}, status=404)

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保 extract_json_from_script_content 函数已定义
        params_json_data = extract_json_from_script_content(content) 
        
        if params_json_data:
            return web.json_response(params_json_data, status=200) # 成功时也使用 web.json_response
        else:
            return web.json_response({"error": f"脚本 '{script_name_param}' 中未找到有效的参数定义JSON块"}, status=404)
    except Exception as e:
        print(f"API端点错误 /get_script_params: {e}\n{traceback.format_exc()}")
        return web.json_response({"error": f"处理脚本参数时发生服务器内部错误: {str(e)}"}, status=500)



# --- 节点注册 ---
NODE_CLASS_MAPPINGS = {
    "便携脚本执行器_JS动态接口": 便携脚本执行器_动态JS
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "便携脚本执行器_JS动态接口": "便携脚本执行器 (JS动态接口)"
}

print("便携脚本执行器 (JS动态接口) Python部分已加载。")

# Updated on: 2025-05-21 23:05:40
