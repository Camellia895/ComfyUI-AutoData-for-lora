# ComfyUI-Nodes/metadata_rule_detector_v3.py
import os
import re

# --- 全局变量和辅助函数 ---
NODE_FILE_DIR = os.path.dirname(__file__)
RULE_FOLDER_NAME = "rules"
RULES_DIR_PATH = os.path.join(NODE_FILE_DIR, RULE_FOLDER_NAME)

# 在节点加载时，预先扫描一次规则文件夹
RULE_FILES = ["[无]"]
if os.path.isdir(RULES_DIR_PATH):
    try:
        rule_filenames = sorted(
            [f for f in os.listdir(RULES_DIR_PATH) if f.endswith(".txt")],
            key=lambda s: [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', s)]
        )
        RULE_FILES.extend(rule_filenames)
    except Exception as e:
        print(f"[元数据规则检测器 V3] 错误: 扫描规则文件夹 '{RULES_DIR_PATH}' 失败: {e}")
else:
    try:
        os.makedirs(RULES_DIR_PATH)
        print(f"[元数据规则检测器 V3] 提示: 已自动创建规则文件夹 '{RULES_DIR_PATH}'。")
    except Exception as e:
        print(f"[元数据规则检测器 V3] 错误: 创建规则文件夹 '{RULES_DIR_PATH}' 失败: {e}")


class 元数据规则检测器_V3:
    """
    元数据规则检测器 (Metadata Rule Detector) V3 -
    根据外部规则文件(.txt)动态检测元数据。
    支持 AND/OR 逻辑，并引入了排除规则 '!' (AND NOT)。
    可选择是否区分大小写，并根据匹配顺序或失败位置输出路由信号。
    """
    
    节点名称 = "元数据规则检测器 V3"
    CATEGORY = "自动数据/utils"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "元数据": ("STRING", {"multiline": True, "default": ""}),
                "规则_1": (RULE_FILES, ),
                "规则_2": (RULE_FILES, ),
                "规则_3": (RULE_FILES, ),
                "规则_4": (RULE_FILES, ),
                "区分大小写": ("BOOLEAN", {
                    "default": True, 
                    "label_on": "是 (严格匹配)", 
                    "label_off": "否 (忽略大小写)"
                }),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("匹配位次",)
    FUNCTION = "detect"

    def _parse_and_check_rule(self, rule_filename: str, metadata_text: str, case_sensitive: bool) -> bool:
        """解析单个规则文件并根据其内容检查元数据，支持排除规则 '!'。"""
        rule_filepath = os.path.join(RULES_DIR_PATH, rule_filename)

        try:
            with open(rule_filepath, 'r', encoding='utf-8') as f:
                # 遍历文件中的每一行（OR条件）
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    include_keywords = []
                    exclude_keywords = []

                    # 分离包含和排除的关键词
                    for keyword in line.split(','):
                        keyword = keyword.strip()
                        if not keyword:
                            continue
                        
                        if keyword.startswith('!'):
                            # 是排除词，去掉 '!' 并存入排除列表
                            exclude_keywords.append(keyword[1:])
                        else:
                            # 是包含词，存入包含列表
                            include_keywords.append(keyword)
                    
                    # 根据 case_sensitive 选项决定是否将关键词转为小写
                    if not case_sensitive:
                        include_keywords = [kw.lower() for kw in include_keywords]
                        exclude_keywords = [kw.lower() for kw in exclude_keywords]

                    # 开始检查当前行的所有条件
                    line_match = True
                    
                    # 1. 检查所有必须包含的词
                    for kw in include_keywords:
                        if kw not in metadata_text:
                            line_match = False
                            break
                    if not line_match:
                        continue # 当前行不匹配，检查下一行

                    # 2. 检查所有必须排除的词
                    for kw in exclude_keywords:
                        if kw in metadata_text:
                            line_match = False
                            break
                    
                    # 如果所有条件都满足，则整行匹配成功，整个文件也匹配成功
                    if line_match:
                        print(f"    - 规则 '{rule_filename}' 匹配成功 (基于行: '{line}')")
                        return True
                        
        except FileNotFoundError:
            print(f"[{self.节点名称}] 警告: 规则文件 '{rule_filename}' 未找到。")
            return False
        except Exception as e:
            print(f"[{self.节点名称}] 错误: 读取或解析规则文件 '{rule_filename}' 失败: {e}")
            return False
            
        return False

    def detect(self, 元数据: str, 规则_1: str, 规则_2: str, 规则_3: str, 规则_4: str, 区分大小写: bool):
        print(f"\n[{self.节点名称}] 节点开始执行...")
        print(f"  > 匹配模式: {'区分大小写' if 区分大小写 else '忽略大小写'}")
        
        search_text = 元数据 if 区分大小写 else 元数据.lower()
        selected_rules = [规则_1, 规则_2, 规则_3, 规则_4]
        
        for i, rule_name in enumerate(selected_rules):
            current_position = i + 1
            print(f"  > 正在检测位次 {current_position}: 选择的规则是 '{rule_name}'")

            if rule_name == "[无]":
                print(f"[{self.节点名称}] 在位次 {current_position} 遇到 '[无]' 选项。流程结束。")
                print(f"  > 输出: {current_position}")
                return (current_position,)
            
            match_found = self._parse_and_check_rule(rule_name, search_text, 区分大小写)
            
            if match_found:
                print(f"[{self.节点名称}] 成功匹配！")
                print(f"  > 输出: {current_position}")
                return (current_position,)

        print(f"[{self.节点名称}] 所有四个配置的规则均未匹配成功。")
        print(f"  > 输出: 5")
        return (5,)

# --- 节点注册 ---
NODE_CLASS_MAPPINGS = {
    "MetadataRuleDetector_AutoData_V3_CN": 元数据规则检测器_V3
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "MetadataRuleDetector_AutoData_V3_CN": "元数据规则检测器[自动数据]"
}