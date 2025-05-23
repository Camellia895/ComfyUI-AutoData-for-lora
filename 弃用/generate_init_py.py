import os

def generate_init_py():
    """
    自动生成或更新当前目录下的 __init__.py 文件，
    使其能够导入并合并所有其他节点文件中定义的节点。
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    init_py_path = os.path.join(current_dir, "__init__.py")

    node_files = []
    # 扫描当前目录下的所有 .py 文件
    for filename in os.listdir(current_dir):
        # 排除 __init__.py 自身和 generate_init_py.py 脚本自身
        if filename.endswith(".py") and filename not in ["__init__.py", "generate_init_py.py"]:
            node_files.append(filename)

    if not node_files:
        print("未找到任何节点文件（*.py，排除 __init__.py 和 generate_init_py.py）。__init__.py 将被清空或不生成任何节点导入。")
        with open(init_py_path, "w", encoding="utf-8") as f:
            f.write("# __init__.py: 此文件由 generate_init_py.py 自动生成\n")
            f.write("# 未找到任何节点文件，所以此处为空。\n")
            f.write("NODE_CLASS_MAPPINGS = {}\n")
            f.write("NODE_DISPLAY_NAME_MAPPINGS = {}\n")
        print(f"已更新 {init_py_path} (无节点导入)。")
        return

    # 构建 __init__.py 的内容
    content = [
        "# __init__.py: 此文件由 generate_init_py.py 自动生成",
        "# 请勿手动修改此文件，除非您知道自己在做什么！\n",
        "NODE_CLASS_MAPPINGS = {}",
        "NODE_DISPLAY_NAME_MAPPINGS = {}\n"
    ]

    for i, filename in enumerate(node_files):
        module_name = filename[:-3] # <-- 修正：移除 .py 后缀
        # 确保别名有效，替换文件名中可能的特殊字符为下划线
        # 例如：my-node.py -> my_node
        # 这是一个简单的替换，如果文件名包含更复杂的非字母数字字符，可能需要更精细的处理
        clean_module_name = module_name.replace('-', '_').replace('.', '_')
        map_alias = f"{clean_module_name}_MAP"
        names_alias = f"{clean_module_name}_NAMES"

        # 添加导入语句
        content.append(f"from .{module_name} import NODE_CLASS_MAPPINGS as {map_alias}, NODE_DISPLAY_NAME_MAPPINGS as {names_alias}")

    content.append("\n# 合并所有节点的映射")
    for filename in node_files:
        module_name = filename[:-3] # <-- 修正：移除 .py 后缀
        clean_module_name = module_name.replace('-', '_').replace('.', '_')
        map_alias = f"{clean_module_name}_MAP"
        names_alias = f"{clean_module_name}_NAMES"
        content.append(f"NODE_CLASS_MAPPINGS.update({map_alias})")
        content.append(f"NODE_DISPLAY_NAME_MAPPINGS.update({names_alias})")

    content.append("\n# 打印一条消息，方便确认节点包是否被加载")
    content.append('print("我的自定义节点包: 已成功加载所有节点！")')

    # 将内容写入 __init__.py
    with open(init_py_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    print(f"\n成功生成/更新 {init_py_path} 文件。")
    print("请重启 ComfyUI 以使更改生效。")

if __name__ == "__main__":
    generate_init_py()
    input("按任意键退出...") # 保持窗口打开直到用户按下按键