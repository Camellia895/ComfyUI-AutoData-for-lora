# Last updated: 2025-05-21 19:59:48

# SCRIPT_META_DATA_START
# NAME_ZH: 删除指定后缀文件
# DESCRIPTION_ZH: 删除指定文件夹中所有特定文件后缀的文件。
# ARGS:
#   - name: folder_path
#     type: STRING
#     label_zh: 目标文件夹路径
#     default: ""
#     placeholder_zh: "例如: D:\\ComfyUI\\output"
#   - name: extensions
#     type: STRING
#     label_zh: 文件后缀列表
#     default: "txt,log"
#     placeholder_zh: "用逗号分隔（例如：txt,log,bak）"
# SCRIPT_META_DATA_END

import os
import sys
import time
import argparse

def delete_files_by_extension(folder_path, extensions_str):
    """
    遍历指定文件夹，删除所有具有特定后缀的文件。
    extensions_str 是逗号分隔的字符串，例如 "txt,log,bak"。
    """
    if not os.path.isdir(folder_path):
        print(f"错误: 文件夹未找到或无效: {folder_path}")
        sys.exit(1)

    if not extensions_str:
        print("错误: 未提供要删除的文件后缀。")
        sys.exit(1)
    
    target_extensions = {f".{ext.strip().lower()}" for ext in extensions_str.split(',') if ext.strip()}
    if not target_extensions:
        print("错误: 提供的文件后缀列表无效。")
        sys.exit(1)

    deleted_count = 0
    skipped_count = 0
    error_count = 0

    print(f"开始扫描文件夹: {folder_path}，查找具有后缀 {extensions_str} 的文件...")

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in target_extensions:
                file_path = os.path.join(root, file)
                try:
                    time.sleep(0.05)
                    os.remove(file_path)
                    print(f"已删除: {file_path}")
                    deleted_count += 1
                except OSError as e:
                    print(f"错误: 无法删除文件 '{file_path}' (可能被占用或权限问题): {e}")
                    error_count += 1
                except Exception as e:
                    print(f"错误: 删除文件 '{file_path}' 时发生意外错误: {e}")
                    error_count += 1
            else:
                skipped_count += 1

    summary_message = f"操作完成。删除匹配文件: {deleted_count} 个, 跳过文件: {skipped_count} 个, 发生错误: {error_count} 个。"
    print(summary_message)

    if error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="删除指定文件夹中所有特定文件后缀的文件。")
    # folder_path 和 extensions 都改为可选，这样在没有参数时可以提示输入
    parser.add_argument("folder_path", type=str, nargs='?', help="要清理的文件夹路径。")
    parser.add_argument("extensions", type=str, nargs='?', help="要删除的文件后缀，用逗号分隔（例如：txt,log）。")
    
    args = parser.parse_args(sys.argv[1:])

    folder_path = args.folder_path
    extensions = args.extensions

    # 如果通过双击运行（没有提供参数），则提示用户输入
    if folder_path is None or extensions is None:
        print("您正在通过双击运行此脚本，请提供所需参数。")
        while True:
            user_input_folder = input("请输入要清理的文件夹路径 (例如: D:\\ComfyUI\\output): ")
            if user_input_folder:
                folder_path = user_input_folder.strip()
                break
            else:
                print("文件夹路径不能为空，请重新输入。")
        
        while True:
            user_input_ext = input("请输入要删除的文件后缀（逗号分隔，例如：txt,log,bak）: ")
            if user_input_ext:
                extensions = user_input_ext.strip()
                break
            else:
                print("文件后缀不能为空，请重新输入。")

    # 执行主函数
    delete_files_by_extension(folder_path, extensions)

    # 脚本执行完毕后暂停，以便用户查看输出
    input("按任意键退出...")

# Updated on: 2025-05-21 19:59:48
