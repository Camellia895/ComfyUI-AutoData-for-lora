import os
import importlib
import inspect
import traceback

NODE_PACK_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_PACKAGE_NAME = __name__ # Should be the name of your package, e.g., "ComfyUI_AutoMask"

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

print(f"### 初始化自定义节点: {CURRENT_PACKAGE_NAME} ###")
print(f"    节点包根目录: {NODE_PACK_DIR}")
print(f"    当前包名 (__name__): {CURRENT_PACKAGE_NAME}")

# 遍历节点包根目录下的所有文件
for filename in os.listdir(NODE_PACK_DIR):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name_only = filename[:-3]
        relative_module_path = f".{module_name_only}"
        
        try:
            print(f"    尝试导入模块: '{relative_module_path}' (从包 '{CURRENT_PACKAGE_NAME}')")
            module = importlib.import_module(relative_module_path, package=CURRENT_PACKAGE_NAME)

            # --- 优先级 1: 检查模块是否已定义自己的映射 ---
            module_has_explicit_mappings = False
            if hasattr(module, 'NODE_CLASS_MAPPINGS') and isinstance(getattr(module, 'NODE_CLASS_MAPPINGS'), dict):
                module_class_map = getattr(module, 'NODE_CLASS_MAPPINGS')
                module_display_map = getattr(module, 'NODE_DISPLAY_NAME_MAPPINGS', {}) # 可能是dict或不存在
                if not isinstance(module_display_map, dict): # 确保是字典
                    module_display_map = {}

                print(f"      > 模块 '{module_name_only}' 包含显式的 NODE_CLASS_MAPPINGS。优先使用。")
                for mapping_key, class_obj in module_class_map.items():
                    if mapping_key in NODE_CLASS_MAPPINGS:
                        print(f"        ! 警告: 映射键 '{mapping_key}' 已存在于全局映射中。可能存在冲突。来自模块 '{module_name_only}' 的定义将覆盖。")
                    
                    NODE_CLASS_MAPPINGS[mapping_key] = class_obj
                    
                    # 确定显示名称
                    display_name = module_display_map.get(mapping_key) # 首先从模块的显示映射中获取
                    if display_name is None: # 如果模块的显示映射中没有
                        display_name = getattr(class_obj, 'NODE_NAME', None) or \
                                       getattr(class_obj, 'DISPLAY_NAME', None) or \
                                       mapping_key # 最后回退到映射键或类名 (如果可获得)
                    
                    NODE_DISPLAY_NAME_MAPPINGS[mapping_key] = display_name
                    category = getattr(class_obj, 'CATEGORY', '未知 (来自显式映射)')
                    print(f"        + (显式) 已注册节点: {mapping_key} -> UI: '{display_name}' (分类: '{category}')")
                module_has_explicit_mappings = True

            # --- 优先级 2: 如果模块没有显式映射，则进行自动类发现 ---
            if not module_has_explicit_mappings:
                print(f"      > 模块 '{module_name_only}' 未包含显式映射。尝试自动发现节点类。")
                for member_name, member_obj in inspect.getmembers(module):
                    if inspect.isclass(member_obj) and member_obj.__module__ == module.__name__:
                        if hasattr(member_obj, "INPUT_TYPES") and \
                           hasattr(member_obj, "FUNCTION") and \
                           hasattr(member_obj, "CATEGORY"):

                            class_name_str = member_obj.__name__
                            # 使用类名作为默认的内部映射键
                            # 如果担心不同模块中的同名类冲突，可以加入模块名前缀
                            # mapping_key = f"{module_name_only}_{class_name_str}" 
                            mapping_key = class_name_str # 当前使用类名

                            if mapping_key in NODE_CLASS_MAPPINGS:
                                print(f"        ! 警告: 自动发现的映射键 '{mapping_key}' 已存在。可能存在冲突。来自模块 '{module_name_only}' 的 '{class_name_str}' 将覆盖。")

                            NODE_CLASS_MAPPINGS[mapping_key] = member_obj
                            
                            display_name = getattr(member_obj, 'NODE_NAME', None) or \
                                           getattr(member_obj, 'DISPLAY_NAME', None) or \
                                           class_name_str
                            
                            NODE_DISPLAY_NAME_MAPPINGS[mapping_key] = display_name
                            category = getattr(member_obj, 'CATEGORY', '未知分类')
                            print(f"        + (自动) 已注册节点: {mapping_key} -> UI: '{display_name}' (分类: '{category}')")
            
        except ImportError as e:
            print(f"[错误] 从包 '{CURRENT_PACKAGE_NAME}' 导入模块 '{module_name_only}' 失败: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"[错误] 处理来自包 '{CURRENT_PACKAGE_NAME}' 的模块 '{module_name_only}' 时发生意外错误: {e}")
            traceback.print_exc()

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print(f"### {CURRENT_PACKAGE_NAME}: 完成处理，总共注册 {len(NODE_CLASS_MAPPINGS)} 个节点。")
if not NODE_CLASS_MAPPINGS and any(f.endswith(".py") and f != "__init__.py" for f in os.listdir(NODE_PACK_DIR)):
    print(f"    警告: 未能从 {CURRENT_PACKAGE_NAME} 加载任何节点。请检查错误信息和节点文件结构。")
print("----------------------------------------------------")