import os
import glob
# import PIL, numpy, torch 
# 这些导入对于计数节点不是必需的，如果你是追加到image_reader_node.py中，它们已经存在。

class FileCounterInFolder:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义节点的输入类型。
        """
        return {
            "required": {
                # 文件夹路径输入
                "folder_path": ("STRING", {
                    "default": "请在此输入要计数的文件夹路径",
                    "multiline": False
                }),
                # 文件后缀输入，用户可以指定多个，用逗号分隔
                "file_extension": ("STRING", {
                    "default": ".png, .jpg, .jpeg", # 默认常见的图片后缀
                    "multiline": False,
                    "placeholder": "例如: .png, .jpg, .json" # 提示用户如何输入
                }),
                # 是否递归查找子文件夹
                "recursive": ("BOOLEAN", {
                    "default": False # 默认不递归
                })
            }
        }

    # 定义节点的返回类型（输出）
    RETURN_TYPES = ("INT",)
    # 定义节点输出的名称
    RETURN_NAMES = ("文件个数",)
    # 指定节点执行时调用的函数
    FUNCTION = "count_files"
    # 定义节点在ComfyUI菜单中的分类
    CATEGORY = "我的文件工具" # 可以和之前的节点放在同一个分类，或者创建新分类

    def count_files(self, folder_path, file_extension, recursive):
        """
        节点的核心逻辑函数。
        根据输入的文件夹路径、文件后缀和是否递归查找，计算文件个数。
        """
        # 检查文件夹路径是否存在
        if not os.path.isdir(folder_path):
            raise ValueError(f"文件夹未找到: {folder_path}")

        # 将输入的后缀字符串分割成列表，并去除空格，确保每个后缀以点开头
        extensions = [ext.strip() for ext in file_extension.split(',') if ext.strip()]
        # 确保每个后缀都有前导点，如果用户忘记输入
        extensions = [ext if ext.startswith('.') else '.' + ext for ext in extensions]

        file_count = 0
        
        if recursive:
            # 递归查找
            for root, _, files in os.walk(folder_path):
                for file in files:
                    # 检查文件是否以任何一个指定的后缀结尾
                    if any(file.lower().endswith(ext.lower()) for ext in extensions):
                        file_count += 1
        else:
            # 非递归查找（只查找当前文件夹）
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path): # 确保是文件而不是文件夹
                    # 检查文件是否以任何一个指定的后缀结尾
                    if any(filename.lower().endswith(ext.lower()) for ext in extensions):
                        file_count += 1

        print(f"在 '{folder_path}' 中找到了 {file_count} 个文件，后缀为 {file_extension} (递归: {recursive})")
        return (file_count,)



# ComfyUI用来注册节点的字典。
# 请确保你的所有节点类都在这里注册。
NODE_CLASS_MAPPINGS = {
    # 如果你已经有了 ImageReaderByIndex，这里需要追加
    # "ImageReaderByIndex": ImageReaderByIndex,
    "FileCounterInFolder": FileCounterInFolder
}

# ComfyUI用来显示节点的用户友好名称的字典。
# 请确保你的所有节点显示名称都在这里注册。
NODE_DISPLAY_NAME_MAPPINGS = {
    # 如果你已经有了 ImageReaderByIndex，这里需要追加
    # "ImageReaderByIndex": "按索引读取图片",
    "FileCounterInFolder": "文件夹文件计数" # 节点在ComfyUI菜单中显示的名称
}