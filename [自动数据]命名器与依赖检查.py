#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI节点批量修改脚本
用于给节点添加[自动数据]后缀并修改分类
"""

import os
import re
import ast
import sys
from typing import List, Dict, Tuple, Optional

class NodeModifier:
    def __init__(self, folder_path: str = "."):
        self.folder_path = folder_path
        self.modified_files = []
        self.dependencies = set()
        
    def scan_python_files(self) -> List[str]:
        """扫描文件夹中的Python文件"""
        python_files = []
        for file in os.listdir(self.folder_path):
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(self.folder_path, file))
        return python_files
    
    def analyze_imports(self, content: str) -> None:
        """分析文件中的import语句，收集依赖"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not alias.name.startswith('.') and alias.name not in ['os', 'sys', 'json', 'math', 'random']:
                            self.dependencies.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not node.module.startswith('.'):
                        if node.module not in ['os', 'sys', 'json', 'math', 'random', 'typing']:
                            self.dependencies.add(node.module)
        except:
            pass
    
    def find_node_mappings(self, content: str) -> List[Tuple[str, int, int]]:
        """查找NODE_CLASS_MAPPINGS定义"""
        mappings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 查找NODE_CLASS_MAPPINGS的定义
            if 'NODE_CLASS_MAPPINGS' in line and '=' in line:
                # 找到完整的字典定义
                brace_count = 0
                start_line = i
                mapping_lines = []
                
                for j in range(i, len(lines)):
                    current_line = lines[j]
                    mapping_lines.append(current_line)
                    
                    # 计算大括号
                    brace_count += current_line.count('{') - current_line.count('}')
                    
                    if brace_count == 0 and '{' in ''.join(mapping_lines):
                        mappings.append(('\n'.join(mapping_lines), start_line, j))
                        break
                        
        return mappings
    
    def find_display_name_mappings(self, content: str) -> List[Tuple[str, int, int]]:
        """查找NODE_DISPLAY_NAME_MAPPINGS定义"""
        mappings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if 'NODE_DISPLAY_NAME_MAPPINGS' in line and '=' in line:
                brace_count = 0
                start_line = i
                mapping_lines = []
                
                for j in range(i, len(lines)):
                    current_line = lines[j]
                    mapping_lines.append(current_line)
                    
                    brace_count += current_line.count('{') - current_line.count('}')
                    
                    if brace_count == 0 and '{' in ''.join(mapping_lines):
                        mappings.append(('\n'.join(mapping_lines), start_line, j))
                        break
                        
        return mappings
    
    def modify_display_names(self, mapping_content: str) -> str:
        """修改显示名称，添加[自动数据]后缀"""
        # 使用正则表达式查找和替换显示名称
        def replace_name(match):
            key = match.group(1)
            quote_char = match.group(2)  # 引号类型 ' 或 "
            name = match.group(3)
            
            # 检查是否已经有自动数据相关的后缀
            if '[自动数据]' in name:
                return match.group(0)  # 已经有[自动数据]，不修改
            elif '自动数据' in name:
                # 有"自动数据"但没有方括号，替换为[自动数据]
                name = re.sub(r'[（(]?自动数据[）)]?', '[自动数据]', name)
            else:
                # 没有自动数据，添加[自动数据]
                name = name + '[自动数据]'
            
            return f'{key}: {quote_char}{name}{quote_char}'
        
        # 匹配字典中的键值对，值是字符串
        pattern = r'(["\'][\w\s]+["\'])\s*:\s*(["\'])(.*?)\2'
        modified_content = re.sub(pattern, replace_name, mapping_content)
        
        return modified_content
    
    def find_class_definitions(self, content: str) -> List[Tuple[str, int, int]]:
        """查找类定义和其中的CATEGORY属性"""
        classes_with_category = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 查找类定义
            if line.startswith('class ') and ':' in line:
                class_start = i
                indent_level = len(lines[i]) - len(lines[i].lstrip())
                
                # 查找类的结束和CATEGORY定义
                j = i + 1
                category_found = False
                category_line = -1
                
                while j < len(lines):
                    current_line = lines[j]
                    current_indent = len(current_line) - len(current_line.lstrip())
                    
                    # 如果缩进回到类级别或更少，类定义结束
                    if current_line.strip() and current_indent <= indent_level:
                        break
                    
                    # 查找CATEGORY定义
                    if 'CATEGORY' in current_line and '=' in current_line:
                        category_found = True
                        category_line = j
                    
                    j += 1
                
                if category_found:
                    classes_with_category.append((lines[class_start:j], class_start, j-1, category_line))
                
                i = j
            else:
                i += 1
                
        return classes_with_category
    
    def modify_category(self, class_content: List[str], category_line_idx: int) -> List[str]:
        """修改类中的CATEGORY属性"""
        modified_content = class_content.copy()
        category_line = modified_content[category_line_idx]
        
        # 替换CATEGORY为"自动数据"
        if '=' in category_line:
            before_equals = category_line.split('=')[0]
            # 保持原有的缩进和格式
            indent = len(category_line) - len(category_line.lstrip())
            CATEGORY = "自动数据"
        
        return modified_content
    
    def process_file(self, file_path: str) -> bool:
        """处理单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except:
                print(f"无法读取文件: {file_path}")
                return False
        
        original_content = content
        modified = False
        
        # 分析依赖
        self.analyze_imports(content)
        
        # 修改NODE_DISPLAY_NAME_MAPPINGS
        display_mappings = self.find_display_name_mappings(content)
        for mapping_content, start_line, end_line in reversed(display_mappings):
            modified_mapping = self.modify_display_names(mapping_content)
            if modified_mapping != mapping_content:
                lines = content.split('\n')
                lines[start_line:end_line+1] = modified_mapping.split('\n')
                content = '\n'.join(lines)
                modified = True
        
        # 修改类中的CATEGORY
        classes = self.find_class_definitions(content)
        for class_content, start_line, end_line, category_line in reversed(classes):
            relative_category_line = category_line - start_line
            modified_class = self.modify_category(class_content, relative_category_line)
            if modified_class != class_content:
                lines = content.split('\n')
                lines[start_line:end_line+1] = modified_class
                content = '\n'.join(lines)
                modified = True
        
        # 如果没有NODE_DISPLAY_NAME_MAPPINGS，尝试从NODE_CLASS_MAPPINGS创建
        if not display_mappings:
            class_mappings = self.find_node_mappings(content)
            if class_mappings:
                # 在文件末尾添加NODE_DISPLAY_NAME_MAPPINGS
                for mapping_content, _, _ in class_mappings:
                    try:
                        # 提取类名并创建显示名称映射
                        import_match = re.findall(r'["\'](\w+)["\']', mapping_content)
                        if import_match:
                            display_mapping_lines = ["\n# 节点显示名称映射"]
                            display_mapping_lines.append("NODE_DISPLAY_NAME_MAPPINGS = {")
                            
                            for class_name in import_match:
                                display_name = f"{class_name}[自动数据]"
                                display_mapping_lines.append(f'    "{class_name}": "{display_name}",')
                            
                            display_mapping_lines.append("}")
                            
                            content += '\n' + '\n'.join(display_mapping_lines)
                            modified = True
                            break
                    except:
                        pass
        
        # 保存修改后的文件
        if modified:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.modified_files.append(file_path)
                print(f"已修改: {file_path}")
                return True
            except:
                print(f"保存文件失败: {file_path}")
                return False
        else:
            print(f"无需修改: {file_path}")
            return False
    
    def generate_requirements(self) -> None:
        """生成requirements.txt文件"""
        if not self.dependencies:
            return
            
        requirements_path = os.path.join(self.folder_path, 'requirements.txt')
        
        # 常见的Python内置库，不需要安装
        builtin_modules = {
            'os', 'sys', 'json', 'math', 'random', 'typing', 're', 'ast',
            'collections', 'functools', 'itertools', 'datetime', 'time',
            'pathlib', 'urllib', 'http', 'logging', 'threading', 'multiprocessing'
        }
        
        # 过滤掉内置模块
        external_deps = [dep for dep in self.dependencies if dep not in builtin_modules]
        
        if external_deps:
            try:
                with open(requirements_path, 'w', encoding='utf-8') as f:
                    for dep in sorted(external_deps):
                        f.write(f"{dep}\n")
                print(f"已生成 requirements.txt，包含 {len(external_deps)} 个依赖")
            except:
                print("生成 requirements.txt 失败")
        else:
            print("未发现外部依赖，无需生成 requirements.txt")
    
    def run(self) -> None:
        """运行脚本"""
        print("开始扫描ComfyUI节点文件...")
        python_files = self.scan_python_files()
        
        if not python_files:
            print("未找到Python文件")
            return
        
        print(f"找到 {len(python_files)} 个Python文件")
        
        success_count = 0
        for file_path in python_files:
            if self.process_file(file_path):
                success_count += 1
        
        print(f"\n处理完成!")
        print(f"成功修改 {success_count} 个文件")
        print(f"修改的文件: {', '.join([os.path.basename(f) for f in self.modified_files])}")
        
        # 生成requirements.txt
        self.generate_requirements()

def main():
    """主函数"""
    # 获取脚本所在目录或用户指定目录
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(folder_path):
        print(f"目录不存在: {folder_path}")
        return
    
    print(f"处理目录: {folder_path}")
    
    modifier = NodeModifier(folder_path)
    modifier.run()

if __name__ == "__main__":
    main()