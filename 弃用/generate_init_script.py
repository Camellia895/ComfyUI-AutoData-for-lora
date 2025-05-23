import os
import sys
import importlib.util # 用于动态导入模块
import shutil # 用于文件操作，如备份
import time # 用于在生成的文件中添加时间戳
from collections import OrderedDict # 有序字典，确保映射顺序相对固定

# 当前生成器脚本的文件名 (用来在扫描时排除自己)
GENERATOR_SCRIPT_NAME = os.path.basename(__file__)
INIT_PY_NAME = "__init__.py" # 目标 __init__.py 文件名

def generate_init_file_content(script_dir, found_modules_data):
    """
    生成 __init__.py 文件的内容。
    found_modules_data 是一个包含元组的列表:
        (模块名, 类映射字典, 显示名称映射字典, WEB目录名)
    """
    
    import_lines = [] # 存储所有需要 import 的语句
    # 使用 OrderedDict 来尽量保持映射的顺序，尽管Python字典自3.7起默认有序
    master_class_mappings = OrderedDict() # 汇总所有节点的类映射
    master_display_name_mappings = OrderedDict() # 汇总所有节点的显示名称映射
    web_directories_found = set() # 存储找到的所有 WEB_DIRECTORY 名称 (应该是唯一的)

    # 遍历所有找到的模块数据，收集导入信息和映射
    for module_name, class_map, display_map, web_dir in found_modules_data:
        if not class_map: # 如果模块没有 NODE_CLASS_MAPPINGS，则跳过
            continue

        # 获取模块中需要导入的类名 (这些是类定义的字符串名称)
        class_names_to_import = list(class_map.keys()) 
        if class_names_to_import:
            # 生成形如 from .模块名 import 类名1, 类名2 的导入语句
            import_lines.append(f"from .{module_name} import {', '.join(class_names_to_import)}")
        
        # 聚合类映射和显示名称映射
        for class_name_str, _ in class_map.items(): # class_map 的值是类对象本身，我们这里用类名字符串
            master_class_mappings[class_name_str] = class_name_str # 值将是导入后的类名变量
            
            # 处理显示名称
            if display_map and class_name_str in display_map:
                display_name_val = display_map[class_name_str]
                # 使用 repr() 来确保显示名称是合法的Python字符串字面量，例如处理引号和特殊字符
                master_display_name_mappings[class_name_str] = repr(display_name_val)
            else:
                # 如果某个类没有在 NODE_DISPLAY_NAME_MAPPINGS 中定义，则使用其类名作为显示名称
                master_display_name_mappings[class_name_str] = repr(class_name_str)

        if web_dir: # 如果模块定义了 WEB_DIRECTORY
            web_directories_found.add(web_dir)

    # --- 开始构建 __init__.py 的文件内容 ---
    content = f"# 此文件由 {GENERATOR_SCRIPT_NAME} 于 {time.strftime('%Y-%m-%d %H:%M:%S')} 自动生成\n"
    content += "# 请不要直接修改此文件。如果需要更新，请重新运行生成器脚本。\n\n"

    # 如果没有找到任何有效的节点模块
    if not import_lines and not master_class_mappings:
        content += "# 未找到自定义节点模块，或扫描到的 .py 文件中未定义 NODE_CLASS_MAPPINGS。\n"
        content += "NODE_CLASS_MAPPINGS = {}\n"
        content += "NODE_DISPLAY_NAME_MAPPINGS = {}\n"
        content += "__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']\n"
        return content

    content += "# 从此包中的其他文件导入节点类\n"
    # 使用 set 去重并排序导入语句，使生成文件更整洁
    content += "\n".join(sorted(list(set(import_lines))))
    content += "\n\n"

    content += "NODE_CLASS_MAPPINGS = {\n"
    for class_name_str, imported_class_name_var in master_class_mappings.items():
        # "类名字符串": 类名变量 (导入后)
        content += f"    \"{class_name_str}\": {imported_class_name_var},\n"
    content += "}\n\n"

    content += "NODE_DISPLAY_NAME_MAPPINGS = {\n"
    for class_name_str, display_name_representation in master_display_name_mappings.items():
        # "类名字符串": "显示名称" (已经是 repr 处理过的字符串)
        content += f"    \"{class_name_str}\": {display_name_representation},\n"
    content += "}\n\n"
    
    # 处理 WEB_DIRECTORY
    web_directory_export_line = ""
    if len(web_directories_found) == 1: # 如果只找到一个 WEB_DIRECTORY
        web_directory_export_line = f"WEB_DIRECTORY = \"{list(web_directories_found)[0]}\"\n"
    elif len(web_directories_found) > 1: # 如果找到多个不同的 WEB_DIRECTORY
        content += f"# 警告: 在不同的模块中找到了多个 WEB_DIRECTORY 值: {web_directories_found}\n"
        content += "# ComfyUI 通常期望一个包只有一个 WEB_DIRECTORY。\n"
        content += "# 您可能需要整合您的web资源或只选择一个。\n"
        # 作为默认行为，如果找到多个，则选择按字母顺序排序的第一个
        chosen_web_dir = sorted(list(web_directories_found))[0]
        web_directory_export_line = f"WEB_DIRECTORY = \"{chosen_web_dir}\" # 警告: 发现了多个WEB目录, 已选择 '{chosen_web_dir}' 作为默认值。\n"

    if web_directory_export_line:
        content += web_directory_export_line + "\n"

    # 定义 __all__ 列表，这是Python包的良好实践
    content += "__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']\n"
    if web_directory_export_line: # 如果定义了 WEB_DIRECTORY，也将其加入 __all__
        content += "if 'WEB_DIRECTORY' in locals():\n" # 检查 WEB_DIRECTORY 是否真的在局部变量中定义了
        content += "    __all__.append('WEB_DIRECTORY')\n"
        
    return content

def main():
    # 获取当前脚本所在的目录，这个目录就是我们的自定义节点包的根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"正在目录 '{script_dir}' 中运行 {GENERATOR_SCRIPT_NAME}...")

    found_modules_data = [] # 用于存储从每个有效模块中提取的数据

    # 关键步骤：暂时将脚本所在目录及其父目录（通常是 custom_nodes）添加到 sys.path
    # 这样做是为了让 importlib 能够正确地解析模块间的相对导入（如果存在的话），
    # 并模拟 ComfyUI 加载自定义节点包时的环境。
    original_sys_path = list(sys.path) # 保存原始的 sys.path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    parent_dir = os.path.dirname(script_dir) # 获取父目录 (通常是 custom_nodes)
    if parent_dir not in sys.path:
         sys.path.insert(0, parent_dir)


    print("\n正在扫描Python模块 (节点文件)...")
    # 遍历脚本所在目录中的所有文件
    for filename in os.listdir(script_dir):
        # 只处理 .py 文件，并排除生成器脚本自身和 __init__.py 文件
        if filename.endswith(".py") and filename != GENERATOR_SCRIPT_NAME and filename != INIT_PY_NAME:
            module_name = os.path.splitext(filename)[0] # 获取模块名 (去掉 .py 后缀)
            module_path = os.path.join(script_dir, filename) # 模块的完整路径
            
            print(f"  尝试处理文件: {filename}")
            
            try:
                # 动态导入模块
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None or spec.loader is None:
                    print(f"    无法为 {filename} 创建模块规范 (spec)。正在跳过。")
                    continue
                
                module = importlib.util.module_from_spec(spec) # 根据规范创建模块对象
                
                # 为了让模块内部的相对导入 (如 from . import some_other_module_in_package) 能够工作，
                # 需要设置模块的 __package__ 和 __name__ 属性。
                # 包名就是当前自定义节点文件夹的名称。
                package_name = os.path.basename(script_dir)
                setattr(module, '__package__', package_name)
                if not hasattr(module, '__name__') or module.__name__ != module_name:
                    setattr(module, '__name__', module_name)

                # 在执行模块代码前，将其添加到 sys.modules 中，这对于某些导入场景是必要的
                sys.modules[module_name] = module 
                spec.loader.exec_module(module) # 执行模块代码，使其定义的变量生效
                
                # 从加载的模块中获取必要的映射字典
                class_mappings = getattr(module, "NODE_CLASS_MAPPINGS", {})
                display_name_mappings = getattr(module, "NODE_DISPLAY_NAME_MAPPINGS", {})
                web_directory = getattr(module, "WEB_DIRECTORY", None) # WEB_DIRECTORY 是可选的
                
                if class_mappings: # 只有定义了 NODE_CLASS_MAPPINGS 的模块才被认为是有效的节点模块
                    print(f"    在 {filename} 中找到了 NODE_CLASS_MAPPINGS。")
                    found_modules_data.append((module_name, class_mappings, display_name_mappings, web_directory))
                else:
                    print(f"    在 {filename} 中未找到 NODE_CLASS_MAPPINGS。将不会聚合到 __init__.py 中。")
            
            except ImportError as e: # 捕获导入错误，例如模块依赖了未安装的库
                print(f"    导入错误 (ImportError) {filename}: {e}。请检查脚本中的依赖或错误。")
            except Exception as e: # 捕获其他在处理模块时可能发生的错误
                print(f"    处理错误 (Exception) {filename}: {e}")
            finally:
                # 清理：如果模块是我们动态加载的，从 sys.modules 中移除它。
                # 这有助于避免在多次运行生成器或模块内容发生变化时出现缓存问题。
                if module_name in sys.modules and sys.modules[module_name] == module : 
                    del sys.modules[module_name]

    # 恢复原始的 sys.path
    sys.path = original_sys_path

    if not found_modules_data:
        print("\n未找到合适的节点模块来构建 __init__.py。")
    else:
        print("\n已成功处理所有找到的模块。正在生成 __init__.py 内容...")

    # 生成 __init__.py 的完整内容
    init_content = generate_init_file_content(script_dir, found_modules_data)
    init_filepath = os.path.join(script_dir, INIT_PY_NAME) # __init__.py 的完整路径

    # 如果已存在 __init__.py 文件，则先备份
    if os.path.exists(init_filepath):
        backup_path = init_filepath + ".bak" # 备份文件名，例如 __init__.py.bak
        if os.path.exists(backup_path): # 如果旧的备份文件已存在，则先删除
            try:
                os.remove(backup_path)
            except Exception as e:
                 print(f"  警告: 无法删除旧的备份文件 {backup_path}: {e}")
        try:
            print(f"\n正在将已存在的 '{INIT_PY_NAME}' 备份到 '{backup_path}'...")
            shutil.copy2(init_filepath, backup_path) # copy2 会同时复制文件元数据
        except Exception as e:
            print(f"  创建 '{INIT_PY_NAME}' 的备份文件时出错: {e}")
            # 在这里可以选择是否因为备份失败而停止执行
            # 当前选择继续执行但发出警告
            # return # 如果希望停止，可以取消此行注释

    print(f"正在写入新的 '{INIT_PY_NAME}' 文件...")
    try:
        with open(init_filepath, "w", encoding="utf-8") as f: # 使用 utf-8 编码写入
            f.write(init_content)
        print(f"已成功生成 '{INIT_PY_NAME}'!")
    except Exception as e:
        print(f"  写入 '{INIT_PY_NAME}' 文件时出错: {e}")

    print("\n脚本执行完毕。")

if __name__ == "__main__":
    main()
    # 在双击运行时，保持窗口打开直到用户按键，方便查看输出
    input("按 Enter 键退出程序...") 