import os
import re

# 定义节点类别，我将它放在 "EasyUse/文本操作" 类别下
CATEGORY = "自动数据"

class SaveTextToDictionaryAuto:
    """
    一个 ComfyUI 节点，用于将处理后的文本保存到指定的 TXT 词典文件。
    它会清理输入文本，并追加到文件末尾，同时避免写入重复行。
    """
    
    @classmethod
    def IS_CHANGED(s, text_to_save, folder_path, file_name):
        # 强制节点每次运行时都重新计算，以确保文件操作执行
        return ""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 输入端口的内部名称（Python变量名）保持英文，这是ComfyUI的常见做法
                # 但节点名称和输出名称可以完全自定义为中文
                "text_to_save": ("STRING", {"multiline": True, "default": ""}), 
                "folder_path": ("STRING", {"default": os.path.join(os.getcwd(), "output", "wildcards")}),
                "file_name": ("STRING", {"default": "my_dictionary"}),
            },
            # 如果需要，可以添加一个可选的输出端口来显示操作结果或处理后的文本
            # "optional": {
            #     "output_message": ("STRING", {"forceInput": False, "default": ""}),
            # }
        }

    # 返回类型，这里输出处理后的文本和操作消息（可选）
    RETURN_TYPES = ("STRING", "STRING") 
    # 定义输出端口的中文名称
    RETURN_NAMES = ("处理后文本", "操作状态") 

    FUNCTION = "save_text" # 节点执行的函数名

    def save_text(self, text_to_save, folder_path, file_name):
        """
        核心功能：处理文本并保存到文件。
        """
        
        # 1. 清理输入文本
        processed_text = str(text_to_save).strip() # 确保是字符串类型
        
        # 将所有换行符替换为逗号
        processed_text = processed_text.replace('\n', ',').replace('\r', ',')
        
        # 将逗号前后可能存在的空格去除 (例如 ", , " -> ",")
        processed_text = re.sub(r'\s*,\s*', ',', processed_text)
        
        # 将多个连续的逗号替换为单个逗号 (例如 ",,," -> ",")
        processed_text = re.sub(r',+', ',', processed_text)
        
        # 去除最终处理后的文本开头和结尾的逗号
        processed_text = processed_text.strip(',')
        
        # 如果处理后的文本为空，则不进行写入操作
        if not processed_text:
            return ("", "输入文本为空或处理后为空，未写入任何内容。")

        # 2. 构建文件路径
        # 确保文件名为有效的文件系统名，移除可能引起问题的字符
        safe_file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if not safe_file_name:
            safe_file_name = "my_dictionary" # 如果文件名处理后为空，则使用默认值
            
        full_path = os.path.join(folder_path, f"{safe_file_name}.txt")

        status_message = ""
        try:
            # 确保目录存在，如果不存在则创建
            os.makedirs(folder_path, exist_ok=True)

            # 读取现有行进行去重，使用集合提高查找效率
            existing_lines = set()
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        # 读取时也strip，确保比较的一致性
                        existing_lines.add(line.strip())

            # 检查是否重复
            if processed_text in existing_lines:
                status_message = f"'{processed_text}' 已存在于词典中，未重复写入。"
            else:
                # 以追加模式打开文件并写入新行
                with open(full_path, 'a', encoding='utf-8') as f:
                    f.write(processed_text + '\n')
                status_message = f"成功将 '{processed_text}' 写入到 '{full_path}'"

        except Exception as e:
            status_message = f"写入文件时发生错误: {e}"
            print(f"Error saving text: {e}") # 打印到 ComfyUI 控制台

        # 返回处理后的文本和操作状态消息
        return (processed_text, status_message)

# 映射节点名称到类
NODE_CLASS_MAPPINGS = {
    "SaveTextToDictionaryAuto": SaveTextToDictionaryAuto
}

# 节点在 ComfyUI UI 中显示的名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveTextToDictionaryAuto": "保存文本到词典[自动数据]"
}