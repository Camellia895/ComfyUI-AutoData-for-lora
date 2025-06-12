import os
import glob
from PIL import Image
import sys
import time
import locale as sys_locale # 使用别名，避免与 ComfyUI 内部可能的 'locale' 模块冲突

# --- 语言字符串设置 ---
# 默认使用英文
NODE_DISPLAY_NAME_TEXT = "Auto Clean 1x1 PNG [AutoData]"
CATEGORY_TEXT = "AutoData/Utilities" # 建议更通用的英文分类

INPUT_ANY_DEFAULT_TEXT = True # 这是一个布尔值，不需要翻译

FOLDER_PATH_DEFAULT = "" # 默认值，不显示在UI上，可以留空或英文
FOLDER_PATH_PLACEHOLDER = "Enter folder path here"

RECURSIVE_SCAN_LABEL = "Recursive Scan"
DRY_RUN_LABEL = "Dry Run (no actual deletion)"

RETURN_ACTUAL_DELETED_COUNT_NAME = "Actual Deleted"
RETURN_TOTAL_SCANNED_COUNT_NAME = "Total Scanned"
RETURN_UI_SUMMARY_LOG_NAME = "UI Summary Log"

# 内部日志/控制台消息
MSG_NODE_START_OP = "[ComfyUI Node] Starting 1x1 PNG cleanup operation..."
MSG_TARGET_FOLDER = "[ComfyUI Node] Target folder: {folder_path}"
MSG_RECURSIVE_SCAN = "[ComfyUI Node] Recursive scan: {recursive_scan}"
MSG_DRY_RUN_MODE = "[ComfyUI Node] Dry run mode: {dry_run}"
MSG_ERROR_INVALID_PATH = "[ComfyUI Node] Error: Invalid or unspecified folder path."
MSG_UI_LOG_ERROR_PATH = "Error: Invalid/unspecified path"
MSG_OP_COMPLETED = "[ComfyUI Node] Operation completed. {ui_log}"
MSG_CLEANUP_TOOL_INIT = "[Cleanup Tool] Found {count} PNG files for checking."
MSG_CLEANUP_TOOL_CHECKING_SIZE = "[Cleanup Tool] Checking image dimensions..."
MSG_CLEANUP_TOOL_CHECKED_PROGRESS = "[Cleanup Tool] Checked {current}/{total} files..."
MSG_WARNING_UNIDENTIFIED_IMAGE = "[Cleanup Tool] Warning: Unidentified image file {filepath} (possibly corrupt or not PNG)."
MSG_ERROR_PROCESSING_FILE = "[Cleanup Tool] Error: Unknown error occurred while processing file {filepath}: {error}"
MSG_CLEANUP_TOOL_FOUND_1x1 = "[Cleanup Tool] Found {count} 1x1 pixel PNG files."
MSG_DRY_RUN_INFO = "[Cleanup Tool] Dry run mode, no files will be actually deleted. The following files would be deleted:"
MSG_CLEANUP_TOOL_DELETING = "[Cleanup Tool] Deleting 1x1 pixel PNG files..."
MSG_CLEANUP_TOOL_EXECUTING_DELETE = "[Cleanup Tool] Executing deletion..."
MSG_CLEANUP_TOOL_DELETED_PROGRESS = "[Cleanup Tool] Deleted {current}/{total} files..."
MSG_CLEANUP_TOOL_DELETED_FILE = "[Cleanup Tool] Deleted: {filepath}"
MSG_ERROR_DELETING_FILE = "[Cleanup Tool] Error: Unable to delete file {filepath} - {error}"
MSG_ERROR_UNKNOWN_DELETE = "[Cleanup Tool] Error: Unknown error occurred while deleting file {filepath}: {error}"
MSG_NO_1x1_FOUND = "[Cleanup Tool] No 1x1 pixel PNG files found."
MSG_TEST_TITLE = "--- 1x1 PNG Image Cleanup Script (Standalone Mode) ---"
MSG_TEST_SCRIPT_DIR = "Script directory: {script_dir}"
MSG_TEST_RECURSIVE_PROMPT = "Recursive scan subfolders? (y/n): "
MSG_TEST_DRY_RUN_PROMPT = "Dry run mode? (No actual deletion, report only) (y/n): "
MSG_WARNING_NON_DRY_RUN = "\nWarning: You have selected non-dry run mode! This will permanently delete files. Are you sure you want to continue? (Type 'yes' to confirm): "
MSG_OP_CANCELED = "Operation canceled."
MSG_TEST_START_CLEANUP = "\n[Standalone Run] Starting cleanup..."
MSG_CLEANUP_COMPLETED = "\n--- Cleanup Completed ---"
MSG_TOTAL_SCANNED_SUMMARY = "Total PNG files scanned: {count} "
MSG_ACTUAL_DELETED_SUMMARY = "Actual 1x1 PNG files deleted: {count} "
MSG_DRY_RUN_FOOTER = "(Dry run mode, no files were actually deleted.)"
MSG_PRESS_ANY_KEY = "\nPress any key to exit..."

# 检测系统语言并设置中文（或回退到英文）
current_lang = sys_locale.getdefaultlocale()[0] 

if current_lang and current_lang.startswith("zh"):
    NODE_DISPLAY_NAME_TEXT = "自动清理1x1 PNG[自动数据]"
    # CATEGORY_TEXT = "自动数据/实用工具" # 再次提醒：翻译分类可能影响 ComfyUI Manager 兼容性

    FOLDER_PATH_PLACEHOLDER = "请在此处输入文件夹路径"

    RECURSIVE_SCAN_LABEL = "递归扫描"
    DRY_RUN_LABEL = "试运行模式 (不实际删除)"

    RETURN_ACTUAL_DELETED_COUNT_NAME = "实际删除数量"
    RETURN_TOTAL_SCANNED_COUNT_NAME = "扫描PNG总数"
    RETURN_UI_SUMMARY_LOG_NAME = "UI摘要日志"

    MSG_NODE_START_OP = "[ComfyUI节点] 启动1x1 PNG清理操作..."
    MSG_TARGET_FOLDER = "[ComfyUI节点] 目标文件夹: {folder_path}"
    MSG_RECURSIVE_SCAN = "[ComfyUI节点] 递归扫描: {recursive_scan}"
    MSG_DRY_RUN_MODE = "[ComfyUI节点] 试运行模式: {dry_run}"
    MSG_ERROR_INVALID_PATH = "[ComfyUI节点] 错误：无效或未指定的文件夹路径。"
    MSG_UI_LOG_ERROR_PATH = "错误: 路径无效/未指定"
    MSG_OP_COMPLETED = "[ComfyUI节点] 操作完成. {ui_log}"
    MSG_CLEANUP_TOOL_INIT = "[清理工具] 发现 {count} 个PNG文件待检查."
    MSG_CLEANUP_TOOL_CHECKING_SIZE = "[清理工具] 正在检查图片尺寸..."
    MSG_CLEANUP_TOOL_CHECKED_PROGRESS = "[清理工具] 已检查 {current}/{total} 个文件..."
    MSG_WARNING_UNIDENTIFIED_IMAGE = "[清理工具] 警告: 无法识别图片文件 {filepath} (可能损坏或非PNG)."
    MSG_ERROR_PROCESSING_FILE = "[清理工具] 错误: 处理文件 {filepath} 时发生未知错误: {error}"
    MSG_CLEANUP_TOOL_FOUND_1x1 = "[清理工具] 发现 {count} 个1x1像素的PNG文件."
    MSG_DRY_RUN_INFO = "[清理工具] 试运行模式，不会实际删除文件。以下文件将被删除:"
    MSG_CLEANUP_TOOL_DELETING = "[清理工具] 正在删除1x1像素的PNG文件..."
    MSG_CLEANUP_TOOL_EXECUTING_DELETE = "[清理工具] 正在执行删除..."
    MSG_CLEANUP_TOOL_DELETED_PROGRESS = "[清理工具] 已删除 {current}/{total} 个文件..."
    MSG_CLEANUP_TOOL_DELETED_FILE = "[清理工具] 已删除: {filepath}"
    MSG_ERROR_DELETING_FILE = "[清理工具] 错误: 无法删除文件 {filepath} - {error}"
    MSG_ERROR_UNKNOWN_DELETE = "[清理工具] 错误: 删除文件 {filepath} 时发生未知错误: {error}"
    MSG_NO_1x1_FOUND = "[清理工具] 未发现1x1像素的PNG文件。"
    MSG_TEST_TITLE = "--- 1x1 PNG 图片清理脚本 (独立运行模式) ---"
    MSG_TEST_SCRIPT_DIR = "脚本所在目录: {script_dir}"
    MSG_TEST_RECURSIVE_PROMPT = "是否递归扫描子文件夹？(y/n): "
    MSG_TEST_DRY_RUN_PROMPT = "是否为试运行模式？(不实际删除，只报告) (y/n): "
    MSG_WARNING_NON_DRY_RUN = "\n警告：您已选择非试运行模式！这将永久删除文件。确定要继续吗？(输入 '是' 确认): "
    MSG_OP_CANCELED = "操作已取消。"
    MSG_TEST_START_CLEANUP = "\n[独立运行] 开始清理..."
    MSG_CLEANUP_COMPLETED = "\n--- 清理完成 ---"
    MSG_TOTAL_SCANNED_SUMMARY = "总共扫描PNG文件: {count} 个"
    MSG_ACTUAL_DELETED_SUMMARY = "实际删除1x1 PNG文件: {count} 个"
    MSG_DRY_RUN_FOOTER = "(试运行模式，未实际删除任何文件。)"
    MSG_PRESS_ANY_KEY = "\n按任意键退出..."

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
                # UI上的标签将直接是英文，如果JSON翻译机制有效，会覆盖。
                # 否则，你可能需要决定是让这些标签保持英文还是直接在Python中硬编码中文。
                # 由于我们采用了直接在Python中切换字符串的方式，所以下面是直接使用变量
                "any": ("IMAGE,MASK,LATENT,MODEL,CLIP,VAE,CONDITIONING,STRING,INT,FLOAT", {"default": INPUT_ANY_DEFAULT_TEXT},), # 用于流程控制的信号
                "folder_path": ("STRING", {"default": FOLDER_PATH_DEFAULT, "placeholder": FOLDER_PATH_PLACEHOLDER}),
                "recursive_scan": ("BOOLEAN", {"default": True, "label_on": RECURSIVE_SCAN_LABEL, "label_off": RECURSIVE_SCAN_LABEL}),
                "dry_run": ("BOOLEAN", {"default": True, "label_on": DRY_RUN_LABEL, "label_off": DRY_RUN_LABEL}),
            },
        }

    # 使用全局变量汉化输出名称
    RETURN_TYPES = ("INT", "INT", "STRING",)
    RETURN_NAMES = (RETURN_ACTUAL_DELETED_COUNT_NAME, RETURN_TOTAL_SCANNED_COUNT_NAME, RETURN_UI_SUMMARY_LOG_NAME,)
    FUNCTION = "execute"
    CATEGORY = CATEGORY_TEXT # 节点在ComfyUI UI中的分类
    OUTPUT_NODE = False

    def execute(self, any, folder_path, recursive_scan, dry_run):
        # 核心处理逻辑将在此被调用
        print(MSG_NODE_START_OP)
        print(MSG_TARGET_FOLDER.format(folder_path=folder_path))
        print(MSG_RECURSIVE_SCAN.format(recursive_scan=recursive_scan))
        print(MSG_DRY_RUN_MODE.format(dry_run=dry_run))

        if not folder_path or not os.path.isdir(folder_path):
            print(MSG_ERROR_INVALID_PATH)
            # 返回默认值和错误信息，确保ComfyUI不会崩溃
            return (0, 0, MSG_UI_LOG_ERROR_PATH)

        scanned_count, deleted_count = self._process_png_files(
            folder_path,
            recursive_scan,
            dry_run,
            is_comfyui_node=True
        )

        ui_log = MSG_TOTAL_SCANNED_SUMMARY.format(count=scanned_count) + ", " + MSG_ACTUAL_DELETED_SUMMARY.format(count=deleted_count)
        print(MSG_OP_COMPLETED.format(ui_log=ui_log))
        return (deleted_count, scanned_count, ui_log)

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

        print(MSG_CLEANUP_TOOL_INIT.format(count=len(png_files)))
        scanned_count = len(png_files)
        files_to_delete = []

        # 初始化进度条
        if is_comfyui_node and _comfy_available:
            pbar = comfy.utils.ProgressBar(len(png_files))
        else:
            print(MSG_CLEANUP_TOOL_CHECKING_SIZE)

        for i, filepath in enumerate(png_files):
            if is_comfyui_node and _comfy_available:
                pbar.update_absolute(i, len(png_files))
            elif (i + 1) % 100 == 0 or (i + 1) == len(png_files): # 每100个或最后一个文件更新进度
                print(MSG_CLEANUP_TOOL_CHECKED_PROGRESS.format(current=i+1, total=len(png_files)))

            try:
                # 使用 with 语句确保文件句柄在检查后立即释放，避免文件占用问题
                with Image.open(filepath) as img:
                    width, height = img.size
                    if width == 1 and height == 1:
                        files_to_delete.append(filepath)
            except Image.UnidentifiedImageError:
                print(MSG_WARNING_UNIDENTIFIED_IMAGE.format(filepath=filepath))
            except Exception as e:
                print(MSG_ERROR_PROCESSING_FILE.format(filepath=filepath, error=e))

        deleted_count = 0
        if files_to_delete:
            print(MSG_CLEANUP_TOOL_FOUND_1x1.format(count=len(files_to_delete)))
            if dry_run:
                print(MSG_DRY_RUN_INFO)
                for f in files_to_delete:
                    print(f"  - {f}")
            else:
                print(MSG_CLEANUP_TOOL_DELETING)
                # 再次初始化进度条，用于删除阶段
                if is_comfyui_node and _comfy_available:
                    pbar_delete = comfy.utils.ProgressBar(len(files_to_delete))
                else:
                    print(MSG_CLEANUP_TOOL_EXECUTING_DELETE)

                for j, filepath in enumerate(files_to_delete):
                    if is_comfyui_node and _comfy_available:
                        pbar_delete.update_absolute(j, len(files_to_delete))
                    elif (j + 1) % 10 == 0 or (j + 1) == len(files_to_delete): # 每10个或最后一个文件更新进度
                        print(MSG_CLEANUP_TOOL_DELETED_PROGRESS.format(current=j+1, total=len(files_to_delete)))

                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        print(MSG_CLEANUP_TOOL_DELETED_FILE.format(filepath=filepath))
                    except OSError as e:
                        print(MSG_ERROR_DELETING_FILE.format(filepath=filepath, error=e))
                    except Exception as e:
                        print(MSG_ERROR_UNKNOWN_DELETE.format(filepath=filepath, error=e))
        else:
            print(MSG_NO_1x1_FOUND)

        return scanned_count, deleted_count

# --- 节点注册信息 ---
NODE_CLASS_MAPPINGS = {
    "AutoClean1x1PNG": ScanAndDelete1x1PNG
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoClean1x1PNG": NODE_DISPLAY_NAME_TEXT
}
# --- 节点注册信息结束 ---


# 独立运行模式
if __name__ == "__main__":
    print(MSG_TEST_TITLE)

    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(MSG_TEST_SCRIPT_DIR.format(script_dir=script_dir))

    # 询问是否递归扫描
    recursive_input = input(MSG_TEST_RECURSIVE_PROMPT).lower()
    recursive_scan = recursive_input == 'y'

    # 询问是否为试运行
    dry_run_input = input(MSG_TEST_DRY_RUN_PROMPT).lower()
    dry_run = dry_run_input == 'y'

    if not dry_run:
        confirm = input(MSG_WARNING_NON_DRY_RUN)
        if confirm != '是': # 确保这里是中文“是”
            print(MSG_OP_CANCELED)
            sys.exit(0)

    cleaner = ScanAndDelete1x1PNG()
    print(MSG_TEST_START_CLEANUP)
    scanned_count, deleted_count = cleaner._process_png_files(
        script_dir,
        recursive_scan,
        dry_run,
        is_comfyui_node=False
    )

    print(MSG_CLEANUP_COMPLETED)
    print(MSG_TOTAL_SCANNED_SUMMARY.format(count=scanned_count))
    print(MSG_ACTUAL_DELETED_SUMMARY.format(count=deleted_count))
    if dry_run:
        print(MSG_DRY_RUN_FOOTER)
    
    input(MSG_PRESS_ANY_KEY)