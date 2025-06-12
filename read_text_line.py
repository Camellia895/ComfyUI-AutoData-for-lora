import os
import re
import locale as sys_locale # 使用别名，避免与 ComfyUI 内部可能的 'locale' 模块冲突

# --- 语言字符串设置 ---
# 默认使用英文
NODE_DISPLAY_NAME_TEXT = "Read Text Line by Index [AutoData]"
CATEGORY_TEXT = "AutoData/Text Operations" # 建议更通用的英文分类

FOLDER_PATH_DEFAULT_WILDCARDS = os.path.join(os.getcwd(), "output", "wildcards") # 默认路径，不翻译
FILE_NAME_DEFAULT = "my_dictionary" # 默认文件名，不翻译

RETURN_LINE_CONTENT_NAME = "Line Content"
RETURN_STATUS_MESSAGE_NAME = "Operation Status"
RETURN_TOTAL_LINES_NAME = "Total Lines"

MSG_FILE_NOT_EXISTS = "File does not exist: '{full_path}'"
MSG_FILE_EMPTY = "File is empty, no lines to read."
MSG_INDEX_OUT_OF_RANGE = "Index out of range. Total lines: {total_lines} (Index range 0 to {max_index}), requested index is {line_index}."
MSG_SUCCESS_READ = "Successfully read line at index {line_index}."
MSG_ERROR_READ_FILE = "Error reading file: {error}"
MSG_CONSOLE_ERROR_READ = "Error reading file: {error}" # 内部控制台消息，保持英文或一致

# 检测系统语言并设置中文（或回退到英文）
current_lang = sys_locale.getdefaultlocale()[0] 

if current_lang and current_lang.startswith("zh"):
    NODE_DISPLAY_NAME_TEXT = "按索引读取文本行[自动数据]"
    CATEGORY_TEXT = "自动数据"

    RETURN_LINE_CONTENT_NAME = "行内容"
    RETURN_STATUS_MESSAGE_NAME = "操作状态"
    RETURN_TOTAL_LINES_NAME = "总行数"

    MSG_FILE_NOT_EXISTS = "文件不存在: '{full_path}'"
    MSG_FILE_EMPTY = "文件为空，没有可读取的行。"
    MSG_INDEX_OUT_OF_RANGE = "索引超出范围。文件总行数: {total_lines} (索引范围 0 到 {max_index})，请求索引为 {line_index}。"
    MSG_SUCCESS_READ = "成功读取索引 {line_index} 的行。"
    MSG_ERROR_READ_FILE = "读取文件时发生错误: {error}"
    MSG_CONSOLE_ERROR_READ = "Error reading file: {error}" # 保持英文或根据需求汉化

# --- 语言字符串设置结束 ---

class ReadTextLineByIndex:
    """
    一个 ComfyUI 节点，用于按指定索引从 TXT 文件中读取一行文本。
    """
    
    @classmethod
    def IS_CHANGED(s, folder_path, file_name, line_index):
        # 如果文件路径、文件名或索引改变，强制重新执行
        # 此外，如果文件本身被修改，也应该重新执行
        safe_file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if not safe_file_name: safe_file_name = FILE_NAME_DEFAULT # 使用默认文件名变量
        full_path = os.path.join(folder_path, f"{safe_file_name}.txt")

        if os.path.exists(full_path):
            return str(os.path.getmtime(full_path)) + "_" + str(line_index) 
        return str(line_index) 

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": FOLDER_PATH_DEFAULT_WILDCARDS}),
                "file_name": ("STRING", {"default": FILE_NAME_DEFAULT}),
                "line_index": ("INT", {"default": 0, "min": 0}),
            }
        }

    # 定义输出端口的类型
    RETURN_TYPES = ("STRING", "STRING", "INT") 
    # 定义输出端口的名称，使用变量
    RETURN_NAMES = (RETURN_LINE_CONTENT_NAME, RETURN_STATUS_MESSAGE_NAME, RETURN_TOTAL_LINES_NAME) 

    FUNCTION = "read_line" # 节点执行的函数名
    CATEGORY = CATEGORY_TEXT # 节点在ComfyUI UI中的分类

    def read_line(self, folder_path, file_name, line_index):
        line_content = ""
        status_message = ""
        total_lines = 0

        # 确保文件名为有效的文件系统名，与保存节点保持一致
        safe_file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if not safe_file_name: safe_file_name = FILE_NAME_DEFAULT # 使用默认文件名变量
            
        full_path = os.path.join(folder_path, f"{safe_file_name}.txt")

        if not os.path.exists(full_path):
            status_message = MSG_FILE_NOT_EXISTS.format(full_path=full_path)
            return (line_content, status_message, total_lines)

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()] 
                total_lines = len(lines)

                if total_lines == 0:
                    status_message = MSG_FILE_EMPTY
                elif line_index < 0 or line_index >= total_lines:
                    status_message = MSG_INDEX_OUT_OF_RANGE.format(total_lines=total_lines, max_index=total_lines-1, line_index=line_index)
                else:
                    line_content = lines[line_index]
                    status_message = MSG_SUCCESS_READ.format(line_index=line_index)

        except Exception as e:
            status_message = MSG_ERROR_READ_FILE.format(error=e)
            print(MSG_CONSOLE_ERROR_READ.format(error=e)) # 打印到 ComfyUI 控制台

        # 返回读取到的行内容、操作状态和文件总行数
        return (line_content, status_message, total_lines)

# 映射节点名称到类
NODE_CLASS_MAPPINGS = {
    "ReadTextLineByIndex": ReadTextLineByIndex
}

# 节点在 ComfyUI UI 中显示的名称，使用变量
NODE_DISPLAY_NAME_MAPPINGS = {
    "ReadTextLineByIndex": NODE_DISPLAY_NAME_TEXT
}