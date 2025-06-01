import os
import re

# 注意：CATEGORY 变量通常由你的 __init__.py 负责统一设置，
# 但为了每个节点文件的完整性，这里也可以定义。
# 最终的类别名取决于你的 __init__.py 如何聚合这些信息。
CATEGORY = "自动数据" 

class ReadTextLineByIndex:
    """
    一个 ComfyUI 节点，用于按指定索引从 TXT 文件中读取一行文本。
    """
    
    @classmethod
    def IS_CHANGED(s, folder_path, file_name, line_index):
        # 如果文件路径、文件名或索引改变，强制重新执行
        # 此外，如果文件本身被修改，也应该重新执行
        safe_file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if not safe_file_name: safe_file_name = "my_dictionary"
        full_path = os.path.join(folder_path, f"{safe_file_name}.txt")

        if os.path.exists(full_path):
            # 组合文件修改时间戳和索引来判断是否需要重新执行
            # str(os.path.getmtime(full_path)) 获取文件的最后修改时间戳
            # str(line_index) 确保当索引变化时也触发重新执行
            return str(os.path.getmtime(full_path)) + "_" + str(line_index) 
        # 如果文件不存在，则只依赖于索引来判断是否需要重新执行
        return str(line_index) 

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": os.path.join(os.getcwd(), "output", "wildcards")}),
                "file_name": ("STRING", {"default": "my_dictionary"}),
                "line_index": ("INT", {"default": 0, "min": 0}), # 索引，从0开始，且不能为负数
            }
        }

    # 定义输出端口的类型
    RETURN_TYPES = ("STRING", "STRING", "INT") 
    # 定义输出端口的中文名称
    RETURN_NAMES = ("行内容", "操作状态", "总行数") 

    FUNCTION = "read_line" # 节点执行的函数名

    def read_line(self, folder_path, file_name, line_index):
        line_content = ""
        status_message = ""
        total_lines = 0

        # 确保文件名为有效的文件系统名，与保存节点保持一致
        safe_file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if not safe_file_name: safe_file_name = "my_dictionary"
            
        full_path = os.path.join(folder_path, f"{safe_file_name}.txt")

        if not os.path.exists(full_path):
            status_message = f"文件不存在: '{full_path}'"
            return (line_content, status_message, total_lines)

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()] # 读取所有行并去除行首尾的空白符
                total_lines = len(lines)

                if total_lines == 0:
                    status_message = "文件为空，没有可读取的行。"
                elif line_index < 0 or line_index >= total_lines:
                    status_message = f"索引超出范围。文件总行数: {total_lines} (索引范围 0 到 {total_lines - 1})，请求索引为 {line_index}。"
                else:
                    line_content = lines[line_index]
                    status_message = f"成功读取索引 {line_index} 的行。"

        except Exception as e:
            status_message = f"读取文件时发生错误: {e}"
            print(f"Error reading file: {e}") # 打印到 ComfyUI 控制台

        # 返回读取到的行内容、操作状态和文件总行数
        return (line_content, status_message, total_lines)

# 这个字典是 ComfyUI 自动加载器用来发现节点类的关键。
# 它将 Python 类名（字符串）映射到实际的类对象。
NODE_CLASS_MAPPINGS = {
    "ReadTextLineByIndex": ReadTextLineByIndex
}

# 这个字典是 ComfyUI UI 用来显示节点名称的关键。
# 它将 Python 类名（字符串）映射到你希望在界面上看到的中文名称。
NODE_DISPLAY_NAME_MAPPINGS = {
    "ReadTextLineByIndex": "按索引读取文本行[自动数据]"
}
