import os
import subprocess
import sys
import shutil
import json
import yaml # 导入 PyYAML 库来解析 YAML 格式的元数据

# 注意：PyYAML 通常不是 ComfyUI 默认安装的库。
# 你可能需要手动安装它：
# 1. 打开命令行
# 2. 激活 ComfyUI 的 Python 环境 (例如: G:\ComfyUI_windows_portable\python_embeded\python.exe -m pip install PyYAML)
#    或者直接: pip install PyYAML

# 动态确定当前节点文件所在的目录
CURRENT_NODE_DIR = os.path.dirname(os.path.abspath(__file__))
# 脚本库目录位于当前节点目录下的 portable_scripts 文件夹
PORTABLE_SCRIPTS_DIR = os.path.join(CURRENT_NODE_DIR, "portable_scripts")

class AdvancedFileTool:
    def __init__(self):
        pass

    @classmethod
    def parse_script_metadata(s, script_path):
        """
        解析Python脚本文件，提取其顶部的元数据。
        """
        metadata = {}
        in_metadata_block = False
        metadata_lines = []

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line == "# SCRIPT_META_DATA_START":
                        in_metadata_block = True
                        continue
                    if line == "# SCRIPT_META_DATA_END":
                        break # 结束解析
                    if in_metadata_block:
                        # 移除前面的 '#' 和一个空格
                        if line.startswith("# "):
                            metadata_lines.append(line[2:])
                        elif line.startswith("#"):
                            metadata_lines.append(line[1:])
                        else:
                            # 如果不是注释行，则认为元数据块结束，避免读取到脚本代码
                            break
            
            if not metadata_lines:
                return {"name_zh": os.path.basename(script_path), "description_zh": "无描述", "args": []}

            # 将收集到的元数据行合并成一个字符串，并尝试用 YAML 解析
            # 这里需要替换掉 ARGS: 下面的缩进，使其成为有效的 YAML 列表
            yaml_content = "\n".join(metadata_lines)
            
            # YAML解析，更灵活
            parsed_data = yaml.safe_load(yaml_content)
            
            # 提取并验证数据
            metadata["name_zh"] = parsed_data.get("NAME_ZH", os.path.basename(script_path))
            metadata["description_zh"] = parsed_data.get("DESCRIPTION_ZH", "无描述")
            
            args = []
            raw_args = parsed_data.get("ARGS", [])
            if isinstance(raw_args, list):
                for arg in raw_args:
                    if isinstance(arg, dict) and "name" in arg and "type" in arg:
                        # 确保参数类型是ComfyUI支持的
                        comfyui_type = arg["type"].upper()
                        if comfyui_type not in ["STRING", "INT", "FLOAT", "BOOLEAN", "TEXT", "COMBO", "*"]:
                            print(f"警告: 脚本 '{script_path}' 中参数 '{arg['name']}' 的类型 '{arg['type']}' 不被识别，默认为 STRING。")
                            comfyui_type = "STRING"
                        args.append({
                            "name": arg["name"],
                            "type": comfyui_type,
                            "label_zh": arg.get("label_zh", arg["name"]),
                            "default": arg.get("default", ""),
                            "placeholder_zh": arg.get("placeholder_zh", ""),
                            "multiline": arg.get("multiline", False) # 仅对STRING类型有效
                        })
            metadata["args"] = args

        except FileNotFoundError:
            print(f"错误: 脚本文件未找到: {script_path}")
            return {"name_zh": os.path.basename(script_path), "description_zh": "文件未找到", "args": []}
        except Exception as e:
            print(f"错误: 解析脚本 '{script_path}' 元数据失败: {e}")
            # 如果解析失败，返回默认信息
            return {"name_zh": os.path.basename(script_path), "description_zh": f"元数据解析错误: {e}", "args": []}
        
        return metadata

    @classmethod
    def get_available_scripts(s):
        """
        扫描 portable_scripts 目录，获取所有脚本的元数据。
        """
        # ComfyUI 下拉菜单选项格式: [("internal_value", "Display Name"), ...]
        script_options_for_comfyui = []
        # 脚本详细信息字典，用于内部逻辑 (filename: metadata)
        all_scripts_metadata = {}

        if not os.path.exists(PORTABLE_SCRIPTS_DIR):
            print(f"警告: 便携脚本库目录不存在: {PORTABLE_SCRIPTS_DIR}")
            return [("NO_SCRIPTS_FOLDER", "错误: 脚本库文件夹不存在")], {}

        found_scripts = []
        for filename in os.listdir(PORTABLE_SCRIPTS_DIR):
            if filename.endswith(".py"):
                script_path = os.path.join(PORTABLE_SCRIPTS_DIR, filename)
                if os.path.isfile(script_path):
                    found_scripts.append(filename)
        
        if not found_scripts:
            return [("NO_SCRIPT", "无可用脚本")], {}

        for filename in sorted(found_scripts): # 排序以保证下拉菜单顺序一致
            script_path = os.path.join(PORTABLE_SCRIPTS_DIR, filename)
            metadata = s.parse_script_metadata(script_path)
            
            all_scripts_metadata[filename] = metadata
            script_options_for_comfyui.append((filename, metadata.get("name_zh", filename)))
        
        # 在列表的开头添加一个“请选择”的默认选项
        script_options_for_comfyui.insert(0, ("NO_SCRIPT", "请选择一个脚本"))

        return script_options_for_comfyui, all_scripts_metadata

    @classmethod
    def INPUT_TYPES(s):
        script_options, all_scripts_metadata = s.get_available_scripts()
        default_script_value = script_options[0][0] if script_options else "NO_SCRIPT"

        # 动态生成的输入端口
        # 我们需要一种方法来动态添加端口，但在 INPUT_TYPES 中这很难直接做到。
        # 最常见的做法是预定义一些通用输入，或者依赖于一个“通用参数字符串”
        # 考虑到ComfyUI的节点系统，它不允许在INPUT_TYPES中根据运行时数据动态生成端口。
        # 替代方案：所有参数都通过一个大的“参数字符串”输入，或者预定义多个通用参数输入。
        # 为了兼容性，我们暂时保持“通用参数字符串”的方式，并在工具提示中显示参数描述。

        # 理论上，如果ComfyUI允许，可以这样动态生成：
        # inputs = { "required": { ... } }
        # selected_script_meta = all_scripts_metadata.get(DEFAULT_SELECTED_SCRIPT_AT_LOAD, {})
        # for arg in selected_script_meta.get("args", []):
        #     if arg["type"] == "STRING":
        #         inputs["required"][arg["name"]] = ("STRING", {"default": arg.get("default", ""), "label": arg.get("label_zh", arg["name"])})
        # ...但这不符合INPUT_TYPES的静态定义方式。

        return {
            "required": {
                "trigger_input": ("*", {
                    "tooltip": "连接任何上游节点以触发脚本执行。",
                    "forceInput": True
                }),
                "target_folder": ("STRING", {
                    "default": "请在此输入目标文件夹路径",
                    "multiline": False,
                    "placeholder": "例如: D:\\ComfyUI\\output",
                    "tooltip": "脚本将在此文件夹中执行操作。"
                }),
                "script_to_execute": (script_options, { # 动态下拉菜单
                    "default": default_script_value,
                    "tooltip": "选择要执行的脚本。此列表根据 'portable_scripts' 目录内容自动更新。"
                }),
                "script_arguments": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "脚本的额外命令行参数（不含文件夹路径），用空格分隔，例如：'arg1 \"arg with space\"'。请查阅脚本说明获取所需参数。",
                    "tooltip": s.get_arguments_tooltip(default_script_value, all_scripts_metadata) # 动态工具提示
                }),
                "copy_to_target_folder": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否将脚本复制到目标文件夹执行？这有助于避免文件占用问题。"
                }),
                "delete_script_after_execution": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "执行完毕后，是否从目标文件夹删除复制过去的脚本？（仅当“复制到目标文件夹”为True时有效）"
                }),
                "wait_for_completion": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "如果为True，ComfyUI将等待脚本执行完成并捕获输出；否则，脚本将后台运行且不捕获输出。"
                }),
            },
            "hidden": {
                "extra_pnginfo": ("STRING", {"default": ""})
            }
        }

    @classmethod
    def get_arguments_tooltip(s, selected_script_name, all_scripts_metadata):
        """
        生成 script_arguments 输入的动态工具提示。
        """
        if selected_script_name == "NO_SCRIPT":
            return "请选择一个脚本以查看其参数说明。"
        
        metadata = all_scripts_metadata.get(selected_script_name)
        if not metadata:
            return "无法加载脚本参数信息。"
        
        tooltip = f"脚本 '{metadata['name_zh']}' 的额外参数:\n"
        if metadata.get("description_zh"):
            tooltip += f"描述: {metadata['description_zh']}\n"
        
        args_info = metadata.get("args", [])
        if not args_info:
            tooltip += "此脚本没有额外的命令行参数（除了目标文件夹路径）。"
        else:
            tooltip += "所需参数 (输入到此文本框，用空格分隔):\n"
            for arg in args_info:
                tooltip += f"  - {arg['label_zh']} ({arg['name']}, 类型: {arg['type']})"
                if arg.get("placeholder_zh"):
                    tooltip += f" (例如: {arg['placeholder_zh']})"
                if arg.get("default") != "":
                    tooltip += f" (默认值: {arg['default']})"
                tooltip += "\n"
        tooltip += "\n注意: 目标文件夹路径会自动作为第一个参数传递给脚本。"
        return tooltip


    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("执行结果日志",)
    FUNCTION = "execute_portable_script"
    CATEGORY = "自动数据"

    def execute_portable_script(self, trigger_input, target_folder, script_to_execute,
                                script_arguments, copy_to_target_folder,
                                delete_script_after_execution, wait_for_completion,
                                extra_pnginfo=None):
        """
        核心执行逻辑：复制脚本（如果需要），执行，然后清理（如果需要）。
        """
        log_messages = []

        if script_to_execute == "NO_SCRIPT" or script_to_execute == "NO_SCRIPTS_FOLDER":
            return ("错误: 未选择有效的脚本。",)

        if not os.path.isdir(target_folder):
            return (f"错误: 目标文件夹未找到或无效: {target_folder}",)
        
        source_script_path = os.path.join(PORTABLE_SCRIPTS_DIR, script_to_execute)
        
        if not os.path.exists(source_script_path):
            return (f"错误: 选定的脚本源文件不存在于库中: {source_script_path}",)

        actual_script_to_run_path = source_script_path
        script_was_copied = False

        if copy_to_target_folder:
            target_script_path = os.path.join(target_folder, script_to_execute)
            if not os.path.exists(target_script_path) or not os.path.samefile(source_script_path, target_script_path):
                try:
                    shutil.copy2(source_script_path, target_folder)
                    log_messages.append(f"脚本已复制到目标文件夹: {target_script_path}")
                    actual_script_to_run_path = target_script_path
                    script_was_copied = True
                except Exception as e:
                    return (f"错误: 复制脚本失败 '{source_script_path}' 到 '{target_folder}': {e}",)
            else:
                log_messages.append(f"脚本 '{script_to_execute}' 已存在于目标文件夹且是同一文件，跳过复制。")
                actual_script_to_run_path = target_script_path
        else:
            log_messages.append("未选择复制脚本到目标文件夹，将在脚本库原位置执行。")

        python_executable = sys.executable

        # 构建命令行命令
        # 约定：第一个参数始终是 target_folder
        command = [python_executable, actual_script_to_run_path, target_folder]

        if script_arguments:
            try:
                import shlex
                parsed_args = shlex.split(script_arguments)
                command.extend(parsed_args)
            except Exception as e:
                log_messages.append(f"警告: 解析额外参数失败: {script_arguments} - {e}")

        log_messages.append(f"开始执行脚本: {actual_script_to_run_path}")
        log_messages.append(f"完整命令: {' '.join(command)}")

        try:
            if wait_for_completion:
                process = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
                log_messages.append(f"脚本已完成，退出码: {process.returncode}")
                if process.stdout:
                    log_messages.append("\n--- 脚本标准输出 ---\n" + process.stdout.strip())
                if process.stderr:
                    log_messages.append("\n--- 脚本错误输出 ---\n" + process.stderr.strip())
            else:
                subprocess.Popen(command, text=True, encoding='utf-8', errors='replace')
                log_messages.append("脚本已在后台启动，未等待完成。")

        except subprocess.CalledProcessError as e:
            log_messages.append(f"错误: 脚本执行失败，退出码 {e.returncode}:")
            if e.stdout:
                log_messages.append("\n--- 脚本标准输出 ---\n" + e.stdout.strip())
            if e.stderr:
                log_messages.append("\n--- 脚本错误输出 ---\n" + e.stderr.strip())
        except FileNotFoundError:
            log_messages.append(f"错误: Python 解释器或脚本文件未找到。请检查路径: {python_executable} 或 {actual_script_to_run_path}")
        except Exception as e:
            log_messages.append(f"错误: 执行脚本时发生意外错误: {e}")
        
        if delete_script_after_execution and script_was_copied:
            try:
                time.sleep(0.1)
                os.remove(actual_script_to_run_path)
                log_messages.append(f"已从目标文件夹删除复制的脚本: {actual_script_to_run_path}")
            except Exception as e:
                log_messages.append(f"警告: 删除脚本 '{actual_script_to_run_path}' 失败: {e}")

        return ("\n".join(log_messages),)

NODE_CLASS_MAPPINGS = {
    "AdvancedFileTool": AdvancedFileTool
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedFileTool": "高级文件工具[自动数据]"
}