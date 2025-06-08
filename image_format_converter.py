# ComfyUI-Nodes/image_format_converter_v2.py
import os
from PIL import Image, ImageOps, PngImagePlugin

class 智能格式转换为PNG_V2:
    """
    智能格式转换为PNG (Smart Convert to PNG) V2 -
    接收文件夹和文件名，将图像文件转换为PNG格式，同时尽力保留原始元数据。
    如果输入文件已经是PNG，则智能跳过所有操作。
    """
    
    节点名称 = "智能格式转换为PNG V2"
    CATEGORY = "自动数据/file_utils"

    @classmethod
    def INPUT_TYPES(cls):
        # [修改] 更新输入接口
        return {
            "required": {
                "文件夹路径": ("STRING", {"default": "请填入文件夹路径"}),
                "图片名称": ("STRING", {"default": "请填入带后缀的文件名"}),
                "原始文件处理方式": (["保留 (Keep)", "删除 (Delete)"], {"default": "保留 (Keep)"}),
                "冲突处理": (["跳过 (Skip)", "覆盖 (Overwrite)"], {"default": "跳过 (Skip)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("PNG文件路径", "状态信息")
    FUNCTION = "convert_to_png"

    def convert_to_png(self, 文件夹路径: str, 图片名称: str, 原始文件处理方式: str, 冲突处理: str):
        # 1. [新] 拼接完整的路径
        try:
            完整文件路径 = os.path.join(文件夹路径, 图片名称)
        except TypeError as e:
            error_msg = f"错误: 文件夹路径或图片名称无效，无法拼接。 {e}"
            print(f"[{self.节点名称}] {error_msg}")
            return ("", error_msg)
            
        print(f"\n[{self.节点名称}] 节点开始执行...")
        print(f"  > 目标文件: '{完整文件路径}'")

        # 2. 输入验证
        if not 完整文件路径 or not os.path.isfile(完整文件路径):
            error_msg = f"错误: 文件路径无效或文件不存在 -> '{完整文件路径}'"
            print(f"[{self.节点名称}] {error_msg}")
            return ("", error_msg)

        # 3. 智能PNG检查
        file_base, extension = os.path.splitext(完整文件路径)
        if extension.lower() == ".png":
            status_msg = "输入文件已是PNG，无需转换。直接传出路径。"
            print(f"[{self.节点名称}] {status_msg}")
            return (完整文件路径, status_msg)

        # --- 如果不是PNG，则进入转换流程 ---
        print(f"  > 开始转换非PNG文件: {图片名称}")
        
        # 4. 准备转换路径
        png_output_path = file_base + '.png'

        # 5. 处理文件名冲突
        if os.path.exists(png_output_path) and 冲突处理 == "跳过 (Skip)":
            skip_msg = f"目标PNG文件已存在，已跳过转换: {os.path.basename(png_output_path)}"
            print(f"[{self.节点名称}] {skip_msg}")
            return (png_output_path, skip_msg)
        
        try:
            # 6. 打开图像并读取元数据
            print(f"  > 正在读取图像及元数据...")
            img = Image.open(完整文件路径)
            img = ImageOps.exif_transpose(img)
            
            metadata_to_write = PngImagePlugin.PngInfo()
            if img.info:
                for key, value in img.info.items():
                    if isinstance(value, str):
                        metadata_to_write.add_text(key, value)
                    elif isinstance(value, bytes):
                        metadata_to_write.add_text(key, value.decode('utf-8', 'ignore'))
                print(f"  > 成功读取 {len(img.info)} 条元数据。")
            else:
                print(f"  > 未在原始文件中找到可读的元数据。")

            # 7. 保存为PNG，并写入元数据
            print(f"  > 正在保存为PNG文件: {os.path.basename(png_output_path)}")
            img.save(png_output_path, "PNG", pnginfo=metadata_to_write)
            img.close()

            final_msg = f"成功将 '{图片名称}' 转换为PNG并保留元数据。"

            # 8. 处理原始文件
            if 原始文件处理方式 == "删除 (Delete)":
                try:
                    os.remove(完整文件路径)
                    final_msg += " 原始文件已删除。"
                    print(f"  > 成功删除原始文件: {图片名称}")
                except Exception as e:
                    error_on_delete = f"警告: 转换成功，但删除原始文件失败: {e}"
                    print(f"[{self.节点名称}] {error_on_delete}")
                    final_msg += f" {error_on_delete}"
            
            print(f"[{self.节点名称}] {final_msg}")
            return (png_output_path, final_msg)

        except Exception as e:
            error_msg = f"错误: 在转换过程中发生未知错误: {e}"
            print(f"[{self.节点名称}] {error_msg}")
            if 'img' in locals() and hasattr(img, 'close'):
                img.close()
            return ("", error_msg)

# --- 节点注册 ---
NODE_CLASS_MAPPINGS = {
    "SmartConvertToPNG_AutoData_V2_CN": 智能格式转换为PNG_V2
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SmartConvertToPNG_AutoData_V2_CN": "智能格式转换为PNG V2 [自动数据]"
}