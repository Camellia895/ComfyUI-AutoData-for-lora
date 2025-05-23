import os

class StringConverter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义节点的输入类型。
        """
        return {
            "required": {
                # 文本输入（ComfyUI中的文本框通常是STRING类型，但可能有多行特性）
                "text_input": ("STRING", {
                    "multiline": True, # 允许用户输入多行文本
                    "default": "请在此输入文本"
                }),
                # 字符串输入（典型的单行字符串，用于接收其他节点的STRING输出）
                "string_input": ("STRING", {
                    "multiline": False, # 单行输入
                    "default": "请在此输入字符串"
                }),
            },
            "optional": {
                # 提供一个可选的控制开关，用于确定输出哪个结果
                "output_type_selector": (["文本转字符串", "字符串转文本"], {"default": "文本转字符串"})
            }
        }

    # 定义节点的返回类型（输出）
    # 我们可以根据output_type_selector来动态决定返回哪种类型，但ComfyUI的RETURN_TYPES是静态的。
    # 所以我们定义两个输出，用户根据需要连接其中一个。
    RETURN_TYPES = ("STRING", "STRING",) # 都是STRING类型，只是为了区分用途
    # 定义节点输出的名称
    RETURN_NAMES = ("文本转换后的字符串", "字符串转换后的文本",)
    # 指定节点执行时调用的函数
    FUNCTION = "convert_string"
    # 定义节点在ComfyUI菜单中的分类
    CATEGORY = "自动数据"

    def convert_string(self, text_input, string_input, output_type_selector):
        """
        节点的核心逻辑函数。
        根据选择器将文本转换为字符串，或将字符串转换为文本。
        实际上，都是字符串到字符串的传递，只是在UI层面和概念上做区分。
        """
        # 如果是“文本转字符串”模式
        if output_type_selector == "文本转字符串":
            # 文本输入通常已经是Python字符串，直接返回即可
            # 确保它不是列表（如果上游节点封装了的话，但这节点不会自动解封装）
            # 这里我们假定text_input已经是纯字符串
            print(f"执行 '文本转字符串'：输入: '{text_input}'")
            return (text_input, "") # 返回第一个输出，第二个为空
        # 如果是“字符串转文本”模式
        elif output_type_selector == "字符串转文本":
            # 字符串输入通常已经是Python字符串，直接返回即可
            print(f"执行 '字符串转文本'：输入: '{string_input}'")
            return ("", string_input) # 返回第二个输出，第一个为空

# ComfyUI用来注册节点的字典。
NODE_CLASS_MAPPINGS = {
    "StringConverter": StringConverter
}

# ComfyUI用来显示节点的用户友好名称的字典。
NODE_DISPLAY_NAME_MAPPINGS = {
    "StringConverter": "字符串/文本转换器[自动数据]"
}