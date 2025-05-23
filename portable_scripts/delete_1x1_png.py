# Last updated: 2025-05-21 20:04:32

# SCRIPT_META_DATA_START
# NAME_ZH: 删除1x1像素PNG文件
# DESCRIPTION_ZH: 删除指定文件夹中所有宽高为1像素的.png文件。
# ARGS:
#   - name: folder_path
#     type: STRING
#     label_zh: 目标文件夹路径
#     default: ""
#     placeholder_zh: "例如: D:\\ComfyUI\\output"
# SCRIPT_META_DATA_END

import os
from PIL import Image
import sys
import time
import argparse

def delete_1x1_png_files_in_folder(folder_path):
    """
    遍历指定文件夹，删除所有宽高为1像素的.png文件。
    """
    if not os.path.isdir(folder_path):
        print(f"错误: 文件夹未找到或无效: {folder_path}")
        sys.exit(1)

    deleted_count = 0
    skipped_count = 0
    error_count = 0

    print(f"开始扫描文件夹: {folder_path}，查找宽高为1像素的.png文件...")

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".png"):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        if width == 1 and height == 1:
                            try:
                                time.sleep(0.05)
                                os.remove(file_path)
                                print(f"已删除: {file_path} (1x1 PNG)")
                                deleted_count += 1
                            except OSError as e:
                                print(f"错误: 无法删除文件 '{file_path}' (可能被占用或权限问题): {e}")
                                error_count += 1
                            except Exception as e:
                                print(f"错误: 删除文件 '{file_path}' 时发生意外错误: {e}")
                                error_count += 1
                except Image.UnidentifiedImageError:
                    print(f"警告: 无法识别图像文件格式或文件损坏: {file_path}")
                    error_count += 1
                except FileNotFoundError:
                    print(f"错误: 文件未找到 (可能已被移动或删除): {file_path}")
                    error_count += 1
                except Exception as e:
                    print(f"错误: 处理文件 '{file_path}' 时发生意外错误: {e}")
                    error_count += 1
            else:
                skipped_count += 1

    summary_message = f"操作完成。删除 1x1 PNG 文件: {deleted_count} 个, 跳过非PNG文件: {skipped_count} 个, 发生错误: {error_count} 个。"
    print(summary_message)
    
    if error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    # 使用 argparse 来定义期望的参数
    parser = argparse.ArgumentParser(description="删除指定文件夹中所有宽高为1像素的.png文件。")
    parser.add_argument("folder_path", type=str, nargs='?', help="要清理的文件夹路径。") # nargs='?' 表示参数可选

    # 尝试解析命令行参数
    args = parser.parse_args(sys.argv[1:])

    folder_path = args.folder_path

    # 如果通过双击运行（没有提供参数），则提示用户输入
    if folder_path is None:
        print("您正在通过双击运行此脚本，请提供所需参数。")
        while True:
            user_input = input("请输入要清理的文件夹路径 (例如: D:\\ComfyUI\\output): ")
            if user_input:
                folder_path = user_input.strip()
                break
            else:
                print("文件夹路径不能为空，请重新输入。")
        
        # 为了兼容 argparse 的解析结果，我们将用户输入的值模拟成 args 对象的一个属性
        # 但实际上我们直接使用 folder_path 变量即可

    # 执行主函数
    delete_1x1_png_files_in_folder(folder_path)

    # 脚本执行完毕后暂停，以便用户查看输出
    input("按任意键退出...")

# Updated on: 2025-05-21 20:04:32
