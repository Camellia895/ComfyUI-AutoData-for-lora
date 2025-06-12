import torch
import numpy as np
from PIL import Image
import os
import uuid
import folder_paths

class PassthroughImagePreview:
    """
    一个极简的直通预览节点。
    它利用高级返回格式，在节点内部显示预览图的同时，将原始图像数据传递给输出端口。
    这是基于对 WAS_Image_Save 节点工作原理的分析而构建的。
    """
    # 关键点1：设置 OUTPUT_NODE = True，以获取使用高级返回格式的“资格”。
    OUTPUT_NODE = True
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义节点的输入。"""
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "hidden": {
                # 隐藏的输入，这是为了让 ComfyUI 知道这个节点可以参与工作流的元数据记录
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    # 节点的返回类型
    RETURN_TYPES = ("IMAGE",)
    # 节点的返回端口名称
    RETURN_NAMES = ("图像 (image)",)

    # 节点的主要功能函数
    FUNCTION = "execute"

    # 节点在菜单中的分类
    CATEGORY = "自动数据"

    def execute(self, image: torch.Tensor, prompt=None, extra_pnginfo=None):
        """
        核心执行函数。
        """
        # --- 预览生成逻辑 (与之前类似) ---
        temp_dir = folder_paths.get_temp_directory()
        ui_images_to_preview = []

        for img_tensor in image:
            img_np = np.clip(255. * img_tensor.cpu().numpy(), 0, 255).astype(np.uint8)
            pil_image = Image.fromarray(img_np)
            filename = f"passthrough_preview_{uuid.uuid4()}.png"
            pil_image.save(os.path.join(temp_dir, filename))
            ui_images_to_preview.append({'filename': filename, 'subfolder': '', 'type': 'temp'})
        
        # --- 关键点2：返回特殊的复合字典 ---
        return {
            # "ui" 键负责将预览图信息发送给前端UI
            "ui": {"images": ui_images_to_preview},
            # "result" 键负责将数据打包，发送给节点的输出端口
            "result": (image,) # 注意这个逗号，它确保 (image,) 是一个元组
        }

# ---------------------------------------------------------------------------------
# ComfyUI 节点注册部分
# ---------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "PassthroughImagePreview": PassthroughImagePreview
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PassthroughImagePreview": "直通图像预览 [自动数据]"
}