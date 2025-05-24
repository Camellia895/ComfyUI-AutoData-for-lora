import os
from PIL import Image  # 确保已经通过 pip install Pillow 安装了此库
import sys # 用于获取脚本路径

# --- 配置 ---
MIN_WIDTH = 40  # 图片的最小宽度阈值 (单位: 像素)
MIN_HEIGHT = 40 # 图片的最小高度阈值 (单位: 像素)
# ---

def delete_small_pngs_in_script_directory(min_width, min_height):
    """
    删除脚本自身所在文件夹下所有宽高均小于指定阈值的 .png 文件。
    """
    try:
        # 获取脚本所在的目录
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # 如果是通过 PyInstaller 等工具打包后的 .exe 文件
            script_dir = os.path.dirname(sys.executable)
        else:
            # 如果是直接运行的 .py 文件
            script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # 在某些非常特殊的环境下 __file__ 可能未定义
        print("错误：无法自动确定脚本所在目录。将尝试使用当前工作目录。")
        print("如果这不是您期望的行为，请从命令行使用 'cd' 命令进入目标目录后再运行脚本。")
        script_dir = os.getcwd() # Fallback to current working directory

    print(f"脚本开始处理文件夹: {script_dir}")
    print(f"将删除该文件夹中所有宽度 < {min_width} 像素且高度 < {min_height} 像素的 .png 文件。")
    print("警告：此操作会直接删除文件，且通常不可恢复。建议在操作前备份重要文件。")

    deleted_files_count = 0
    scanned_png_files_count = 0 # 成功打开并检查的PNG文件
    processed_candidate_files = 0 # 扫描到的PNG文件总数
    error_files_count = 0

    try:
        for filename in os.listdir(script_dir):
            # 检查文件扩展名是否为 .png (不区分大小写)
            if filename.lower().endswith(".png"):
                processed_candidate_files += 1
                filepath = os.path.join(script_dir, filename)

                # 确保它是一个文件而不是文件夹
                if os.path.isfile(filepath):
                    try:
                        # 打开图片并获取尺寸
                        # 使用 'with' 语句确保图片文件在使用后被正确关闭
                        with Image.open(filepath) as img:
                            width, height = img.size
                        
                        scanned_png_files_count += 1 # 成功打开并获取尺寸

                        # 检查尺寸是否同时小于阈值
                        if width < min_width and height < min_height:
                            try:
                                os.remove(filepath)
                                print(f"  已删除: {filename} (尺寸: {width}x{height})")
                                deleted_files_count += 1
                            except OSError as e_remove:
                                print(f"  错误: 删除文件 '{filename}' 失败: {e_remove}")
                                error_files_count +=1
                        # else:
                        #     # 如果需要，可以取消注释下面这行来查看哪些文件被跳过了
                        #     print(f"  已跳过 (尺寸不符): {filename} (尺寸: {width}x{height})")

                    except FileNotFoundError:
                        # 这种情况理论上不应该发生，因为 os.listdir 刚列出它
                        print(f"  错误: 文件 '{filename}' 在尝试打开前未找到 (可能在扫描和打开之间被删除)。")
                        error_files_count += 1
                    except Image.UnidentifiedImageError: # Pillow 无法识别图像格式
                        print(f"  警告: 文件 '{filename}' 不是一个有效的PNG图像或已损坏，已跳过。")
                        # 这种情况不算作错误，但也不是成功处理的图片
                    except Exception as e_img: # 其他与图像处理相关的错误
                        print(f"  错误: 无法读取或处理图片文件 '{filename}': {e_img}")
                        error_files_count += 1
    except FileNotFoundError:
        print(f"严重错误：无法访问脚本目录 '{script_dir}'。请检查路径是否存在以及程序是否有权限访问。")
        return # 提前退出函数
    except PermissionError:
        print(f"严重错误：没有权限读取脚本目录 '{script_dir}' 中的文件列表。请检查文件夹权限。")
        return # 提前退出函数


    print("\n--- 处理完成 ---")
    if processed_candidate_files == 0:
        print(f"在脚本所在目录 '{script_dir}' 中没有找到 .png 文件。")
    else:
        print(f"总共扫描到 {processed_candidate_files} 个 .png 候选文件。")
        print(f"成功打开并检查了 {scanned_png_files_count} 个 .png 文件。")
        print(f"其中符合尺寸标准并成功删除的文件数: {deleted_files_count}")
    if error_files_count > 0:
        print(f"处理过程中遇到错误的文件数: {error_files_count}")
    print("--------------------")

if __name__ == "__main__":
    print("脚本已启动...")
    # Pillow库是必需的，再次确认
    try:
        __import__('PIL')
    except ImportError:
        print("错误：Pillow 库未找到。请先安装 Pillow (例如: pip install Pillow)。")
        input("\n按 Enter 键退出程序...")
        sys.exit(1) # 退出脚本

    delete_small_pngs_in_script_directory(MIN_WIDTH, MIN_HEIGHT)

    # 为了让用户在双击运行时能看到输出结果，添加一个 input() 暂停。
    # 如果不需要暂停，可以注释掉下面这行。
    input("\n所有操作已执行完毕。按 Enter 键关闭此窗口...")