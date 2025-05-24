# Last updated: 2025-05-21 23:05:00

# COMFY_NODE_PARAMS_JSON_START #
# {
#   "script_display_name_cn": "简单测试脚本", 
#   "parameters": [
#     {
#       "name": "text_input",
#       "label_cn": "输入文本",
#       "type": "STRING",
#       "default": "默认文本"
#     },
#     {
#       "name": "number_input",
#       "label_cn": "输入数字",
#       "type": "INT",
#       "default": 10,
#       "min": 0,
#       "max": 100
#     }
#   ]
# }
# COMFY_NODE_PARAMS_JSON_END #

import argparse
import time # 只是为了让脚本输出一些东西

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="一个简单的测试脚本，接收文本和数字输入。")
    
    # 这些参数名需要与上面JSON中的 "name" 字段对应
    parser.add_argument("--target_folder", type=str, help="目标文件夹 (由节点传递)") # 假设节点总是传递这个
    parser.add_argument("--text_input", type=str, default="默认文本", help="一个文本输入参数。")
    parser.add_argument("--number_input", type=int, default=10, help="一个数字输入参数。")

    args = parser.parse_args()

    print(f"--- 简单测试脚本开始 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---")
    if args.target_folder:
        print(f"目标文件夹: {args.target_folder}")
    print(f"接收到的文本输入: '{args.text_input}'")
    print(f"接收到的数字输入: {args.number_input}")
    
    # 模拟一些处理
    result = f"文本长度: {len(args.text_input)}, 数字乘以2: {args.number_input * 2}"
    print(result)
    print(f"--- 简单测试脚本结束 ---")

# Updated on: 2025-05-21 23:05:00
