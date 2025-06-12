import json

class A1111MetadataParserPrompts:
    """
    从A1111/Forge风格的JSON元数据中提取提示词。(版本 2.2 - 增强负面提示词检测)
    - 仅当检测到有效负面提示词（长度>=3）时才使用它，否则使用默认值。
    - 根据正面提示词是否存在，输出一个状态码 (1 或 2)。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义节点的输入端口。"""
        return {
            "required": {
                "metadata_json": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "default_negative": ("STRING", {"multiline": False, "default": "", "placeholder": "默认负面提示词..."}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("正面提示词", "负面提示词", "状态 (Status)")

    FUNCTION = "extract_prompts"
    CATEGORY = "自动数据"

    def extract_prompts(self, metadata_json: str, default_negative: str = ""):
        """
        核心解析逻辑。
        """
        parsed_positive = ""
        parsed_negative = ""
        
        try:
            data = json.loads(metadata_json)
            parameters = data.get('parameters', '')

            if parameters:
                split_keyword = '\nNegative prompt: '
                if split_keyword in parameters:
                    parts = parameters.split(split_keyword, 1)
                    parsed_positive = parts[0]
                    negative_part = parts[1]
                    end_of_negative_prompt = negative_part.find('\nSteps: ')
                    
                    if end_of_negative_prompt != -1:
                        parsed_negative = negative_part[:end_of_negative_prompt]
                    else:
                        parsed_negative = negative_part
                else:
                    parsed_positive = parameters
        except (json.JSONDecodeError, AttributeError):
            pass

        # --- 输出逻辑 ---

        # 1. 确定最终的正面提示词
        final_positive = parsed_positive.strip()

        # 2. 【核心逻辑修正】使用您提出的新规则来判断负面提示词是否有效
        # 只有在解析出的负面提示词清理后长度大于等于3时，才认为它是有效的。
        if len(parsed_negative.strip()) >= 10:
            final_negative = parsed_negative.strip()
        else:
            final_negative = default_negative

        # 3. 根据最终的正面提示词生成状态码
        status_code = 1 if final_positive else 2

        # 4. 返回所有三个值
        return (final_positive, final_negative, status_code)

# ---------------------------------------------------------------------------------
# ComfyUI 节点注册部分 (保持不变)
# ---------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "A1111MetadataParserPrompts": A1111MetadataParserPrompts
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "A1111MetadataParserPrompts": "A1111元数据提取提示词"
}