import os
import glob
from PIL import Image
import numpy as np
import torch

class ImageReaderByIndex:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义节点的输入类型。
        这是ComfyUI界面上可以看到的输入参数。
        """
        return {
            "required": {
                # 文件夹路径输入
                "folder_path": ("STRING", {
                    "default": "请在此输入你的图片文件夹路径", # 默认提示文本
                    "multiline": False # 单行输入框
                }),
                # 图片索引输入
                "index": ("INT", {
                    "default": 0,    # 默认从第0张图片开始
                    "min": 0,        # 最小索引值
                    "max": 999999,   # 最大索引值，非常大以适应多数情况
                    "step": 1        # 每次步进1
                }),
                # 排序方式选择
                "sort_order": ([
                    "按名称升序", # name_asc
                    "按名称降序", # name_desc
                    "按时间升序", # time_asc (文件修改时间)
                    "按时间降序"  # time_desc (文件修改时间)
                ],),
            }
        }

    # 定义节点的返回类型（输出）
    RETURN_TYPES = ("IMAGE", "STRING",)
    # 定义节点输出的名称，这些名称会显示在输出端口上
    RETURN_NAMES = ("图片", "图片名称（无后缀）",)
    # 指定节点执行时调用的函数
    FUNCTION = "read_image"
    # 定义节点在ComfyUI菜单中的分类
    CATEGORY = "我的图片工具" # 自定义分类，方便查找

    def read_image(self, folder_path, index, sort_order):
        """
        节点的核心逻辑函数。
        根据输入的文件夹路径、索引和排序方式读取图片。
        """
        # 检查文件夹路径是否存在
        if not os.path.isdir(folder_path):
            raise ValueError(f"文件夹未找到: {folder_path}")

        # 定义支持的图片扩展名
        image_extensions = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.webp"]
        image_files = []
        # 遍历所有扩展名，查找图片文件
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(folder_path, ext)))

        # 如果文件夹中没有找到图片文件
        if not image_files:
            raise ValueError(f"在文件夹中未找到任何图片文件: {folder_path}")

        # 根据选择的排序方式对文件进行排序
        if sort_order == "按名称升序":
            image_files.sort() # 默认按名称升序
        elif sort_order == "按名称降序":
            image_files.sort(reverse=True) # 按名称降序
        elif sort_order == "按时间升序":
            image_files.sort(key=os.path.getmtime) # 按文件修改时间升序
        elif sort_order == "按时间降序":
            image_files.sort(key=os.path.getmtime, reverse=True) # 按文件修改时间降序

        # 检查索引是否越界
        if index < 0 or index >= len(image_files):
            raise IndexError(f"索引 {index} 超出范围。文件夹包含 {len(image_files)} 张图片。")

        # 获取选定图片的完整路径
        selected_image_path = image_files[index]
        # 获取图片名称（不带后缀）
        image_name_without_ext = os.path.splitext(os.path.basename(selected_image_path))[0]

        # 加载图片
        # 使用PIL库打开图片，并转换为RGB模式
        img = Image.open(selected_image_path).convert("RGB")
        # 将PIL图片转换为NumPy数组，并归一化到0-1范围
        img = np.array(img).astype(np.float32) / 255.0
        # 将NumPy数组转换为PyTorch张量，并增加一个批次维度（ComfyUI通常需要）
        img = torch.from_numpy(img)[None,]

        # 返回处理后的图片张量和图片名称
        return (img, image_name_without_ext)

    FUNCTION = "read_image"
    CATEGORY = "我的图片工具" # 或者设置为你统一的类别

# ComfyUI用来注册节点的字典。
# 键是节点的内部名称，值是对应的Python类。
NODE_CLASS_MAPPINGS = {
    "ImageReaderByIndex": ImageReaderByIndex
}

# ComfyUI用来显示节点的用户友好名称的字典。
# 键是节点的内部名称，值是界面上显示的名称。
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageReaderByIndex": "按索引读取图片" # 节点在ComfyUI菜单中显示的名称
}