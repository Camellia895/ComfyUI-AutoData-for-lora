import os
import glob
from PIL import Image
import sys
import time

# 尝试导入ComfyUI的进度条工具，如果不在ComfyUI环境中则跳过
try:
    import comfy.utils
    _comfy_available = True
except ImportError:
    _comfy_available = False

class ScanAndDelete1x1PNG:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "any": ("IMAGE,MASK,LATENT,MODEL,CLIP,VAE,CONDITIONING,STRING,INT,FLOAT", {"default": True},), # 用于流程控制的信号
                "folder_path": ("STRING", {"default": ""},),
                "recursive_scan": ("BOOLEAN", {"default": True},),
                "dry_run": ("BOOLEAN", {"default": True},),
            },

        }

    # 汉化输出名称
    RETURN_TYPES = ("INT", "INT", "STRING",)
    RETURN_NAMES = ("实际删除数量", "扫描PNG总数", "UI摘要日志",) # 对应上面 RETURN_TYPES 的顺序
    FUNCTION = "execute"
    CATEGORY = "自动数据" # 节点在ComfyUI UI中的分类
    OUTPUT_NODE = False

    def execute(self, any, folder_path, recursive_scan, dry_run):
        # 核心处理逻辑将在此被调用
        print(f"\n[ComfyUI节点] 启动1x1 PNG清理操作...")
        print(f"[ComfyUI节点] 目标文件夹: {folder_path}")
        print(f"[ComfyUI节点] 递归扫描: {recursive_scan}")
        print(f"[ComfyUI节点] 试运行模式: {dry_run}")

        if not folder_path or not os.path.isdir(folder_path):
            print("[ComfyUI节点] 错误：无效或未指定的文件夹路径。")
            # 返回默认值和错误信息，确保ComfyUI不会崩溃
            return (0, 0, "错误: 路径无效/未指定")

        scanned_count, deleted_count = self._process_png_files(
            folder_path,
            recursive_scan,
            dry_run,
            is_comfyui_node=True
        )

        # 确保UI日志非常简洁，避免ComfyUI处理extra_pnginfo时的潜在问题
        ui_log = f"扫描:{scanned_count}, 删除:{deleted_count}"
        print(f"[ComfyUI节点] 操作完成. {ui_log}")
        return (deleted_count, scanned_count, ui_log) # 这里的返回顺序与 RETURN_NAMES 对应

    def _process_png_files(self, base_path, recursive, dry_run, is_comfyui_node=False):
        """
        核心处理函数，扫描并处理1x1像素的PNG图片。
        """
        png_files = []
        if recursive:
            # os.walk 递归遍历
            for root, _, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith('.png'):
                        png_files.append(os.path.join(root, file))
        else:
            # 非递归只扫描当前目录
            for file in os.listdir(base_path):
                if file.lower().endswith('.png') and os.path.isfile(os.path.join(base_path, file)):
                    png_files.append(os.path.join(base_path, file))

        print(f"\n[清理工具] 发现 {len(png_files)} 个PNG文件待检查.")
        scanned_count = len(png_files)
        files_to_delete = []

        # 初始化进度条
        if is_comfyui_node and _comfy_available:
            pbar = comfy.utils.ProgressBar(len(png_files))
        else:
            print("[清理工具] 正在检查图片尺寸...")

        for i, filepath in enumerate(png_files):
            if is_comfyui_node and _comfy_available:
                pbar.update_absolute(i, len(png_files))
            elif (i + 1) % 100 == 0 or (i + 1) == len(png_files): # 每100个或最后一个文件更新进度
                print(f"[清理工具] 已检查 {i + 1}/{len(png_files)} 个文件...")

            try:
                # 使用 with 语句确保文件句柄在检查后立即释放，避免文件占用问题
                with Image.open(filepath) as img:
                    width, height = img.size
                    if width == 1 and height == 1:
                        files_to_delete.append(filepath)
            except Image.UnidentifiedImageError:
                print(f"[清理工具] 警告: 无法识别图片文件 {filepath} (可能损坏或非PNG).")
            except Exception as e:
                print(f"[清理工具] 错误: 处理文件 {filepath} 时发生未知错误: {e}")

        deleted_count = 0
        if files_to_delete:
            print(f"\n[清理工具] 发现 {len(files_to_delete)} 个1x1像素的PNG文件.")
            if dry_run:
                print("[清理工具] 试运行模式，不会实际删除文件。以下文件将被删除:")
                for f in files_to_delete:
                    print(f"  - {f}")
            else:
                print("[清理工具] 正在删除1x1像素的PNG文件...")
                # 再次初始化进度条，用于删除阶段
                if is_comfyui_node and _comfy_available:
                    pbar_delete = comfy.utils.ProgressBar(len(files_to_delete))
                else:
                    print("[清理工具] 正在执行删除...")

                for j, filepath in enumerate(files_to_delete):
                    if is_comfyui_node and _comfy_available:
                        pbar_delete.update_absolute(j, len(files_to_delete))
                    elif (j + 1) % 10 == 0 or (j + 1) == len(files_to_delete): # 每10个或最后一个文件更新进度
                        print(f"[清理工具] 已删除 {j + 1}/{len(files_to_delete)} 个文件...")

                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        print(f"[清理工具] 已删除: {filepath}")
                    except OSError as e:
                        print(f"[清理工具] 错误: 无法删除文件 {filepath} - {e}")
                    except Exception as e:
                        print(f"[清理工具] 错误: 删除文件 {filepath} 时发生未知错误: {e}")
        else:
            print("[清理工具] 未发现1x1像素的PNG文件。")

        return scanned_count, deleted_count

# --- 节点注册信息 ---
# 这一部分是关键，它使得外部的 __init__.py 能够自动发现并加载这个节点。
# 每个节点文件都需要定义这些映射。
NODE_CLASS_MAPPINGS = {
    "AutoClean1x1PNG": ScanAndDelete1x1PNG
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoClean1x1PNG": "自动清理1x1 PNG[自动数据]" # 这个是节点在ComfyUI UI中显示的名称
}
# --- 节点注册信息结束 ---


# 独立运行模式
if __name__ == "__main__":
    print("\n--- 1x1 PNG 图片清理脚本 (独立运行模式) ---")

    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"脚本所在目录: {script_dir}")

    # 询问是否递归扫描
    recursive_input = input("是否递归扫描子文件夹？(y/n): ").lower()
    recursive_scan = recursive_input == 'y'

    # 询问是否为试运行
    dry_run_input = input("是否为试运行模式？(不实际删除，只报告) (y/n): ").lower()
    dry_run = dry_run_input == 'y'

    if not dry_run:
        confirm = input("\n警告：您已选择非试运行模式！这将永久删除文件。确定要继续吗？(输入 '是' 确认): ")
        if confirm != '是':
            print("操作已取消。")
            sys.exit(0)

    cleaner = ScanAndDelete1x1PNG()
    print("\n[独立运行] 开始清理...")
    scanned_count, deleted_count = cleaner._process_png_files(
        script_dir,
        recursive_scan,
        dry_run,
        is_comfyui_node=False
    )

    print(f"\n--- 清理完成 ---")
    print(f"总共扫描PNG文件: {scanned_count} 个")
    print(f"实际删除1x1 PNG文件: {deleted_count} 个")
    if dry_run:
        print("(试运行模式，未实际删除任何文件。)")
    
    input("\n按任意键退出...") # 防止命令行窗口立即关闭