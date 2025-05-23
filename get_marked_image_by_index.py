# ComfyUI-AutoData-for-lora/get_marked_image_by_index_v2_cn.py
import os
import re
from PIL import Image, ImageOps
import torch
import numpy as np
import stat

# (pil_to_tensor 和 natural_sort_key 函数保持不变)
def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    image_np = np.array(image).astype(np.float32) / 255.0
    if len(image_np.shape) == 2: image_np = np.expand_dims(image_np, axis=2)
    tensor = torch.from_numpy(image_np)
    if tensor.dim() == 2: tensor = tensor.unsqueeze(2).repeat(1,1,3)
    if tensor.shape[2] == 4: tensor = tensor[:,:,:3]
    tensor = tensor.unsqueeze(0)
    return tensor

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]

class GetMarkedImageByIndexNode_V2_CN:
    def __init__(self):
        pass

    SORT_OPTIONS_VALUES = ["filename_asc", "filename_desc", "modified_time_asc", "modified_time_desc"]
    SORT_OPTIONS_LABELS = [
        "文件名 (升序 A-Z, 0-9)", "文件名 (降序 Z-A, 9-0)",
        "修改时间 (旧->新)", "修改时间 (新->旧)"
    ]

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "请填入文件夹路径"}),
                "search_marker": ("STRING", {"default": "", "multiline": False, "placeholder": "查找包含此符号的文件 (可为空)"}),
                "remove_search_marker_from_name": ("BOOLEAN", {
                    "default": True,
                    "label_on": "是 (从文件名移除搜索标记)",
                    "label_off": "否 (保留搜索标记)"
                }),
                "exclude_marker": ("STRING", {"default": "", "multiline": False, "placeholder": "排除包含此符号的文件 (可为空)"}),
                # "remove_exclude_marker_from_name": ("BOOLEAN", { # 如之前讨论，暂时不实现此项
                # "default": False,
                # "label_on": "是 (从文件名移除排除标记)",
                # "label_off": "否 (保留排除标记)"
                # }),
                "index": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "sort_by": (s.SORT_OPTIONS_LABELS, {"default": s.SORT_OPTIONS_LABELS[0]}), # 使用中文标签显示
                "file_extensions": ("STRING", {"default": "png,jpg,jpeg,webp", "placeholder": "英文逗号分隔, 例如: png,jpg"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "INT", "STRING")
    RETURN_NAMES = ("图像", "文件名", "符合条件总数", "状态信息")
    FUNCTION = "execute"
    CATEGORY = "自动数据" # 保持一致或 "自动数据处理/图像加载 (V2中文)"
    OUTPUT_NODE = False

    def _create_placeholder_image_tensor(self, width=1, height=1) -> torch.Tensor:
        array = np.full((height, width, 3), 0, dtype=np.uint8)
        pil_img = Image.fromarray(array, 'RGB')
        return pil_to_tensor(pil_img)

    def _filter_and_sort_files(self, folder_path, search_marker, remove_search_marker,
                               exclude_marker, sort_by_label, extensions_str):
        
        # 将中文标签映射回内部使用的值
        try:
            sort_by_value = self.SORT_OPTIONS_VALUES[self.SORT_OPTIONS_LABELS.index(sort_by_label)]
        except ValueError:
            sort_by_value = self.SORT_OPTIONS_VALUES[0] # 默认
            print(f"[警告] 无效的排序标签 '{sort_by_label}', 使用默认 '{sort_by_value}'")


        if not folder_path or not os.path.isdir(folder_path):
            return [], "错误: 文件夹路径无效或未指定。"
        
        valid_extensions = {f".{ext.strip().lower()}" for ext in extensions_str.split(',') if ext.strip()}
        if not valid_extensions:
            return [], "错误: 未提供有效的文件扩展名。"

        candidate_files_info = []

        for filename_with_ext in os.listdir(folder_path):
            original_filepath = os.path.join(folder_path, filename_with_ext)
            if os.path.isfile(original_filepath):
                name_part, ext_part = os.path.splitext(filename_with_ext)
                
                if ext_part.lower() not in valid_extensions:
                    continue

                if search_marker and search_marker not in name_part:
                    continue 
                
                if exclude_marker and exclude_marker in name_part:
                    continue 
                
                display_filename_part = name_part
                sort_key_filename_part = name_part

                if search_marker and remove_search_marker:
                    # 移除文件名中的搜索标记（这里简化为替换所有，可以按需调整为只替换末尾或特定位置）
                    display_filename_part = display_filename_part.replace(search_marker, "")
                    sort_key_filename_part = sort_key_filename_part.replace(search_marker, "")
                
                try:
                    modified_time = os.path.getmtime(original_filepath)
                except OSError:
                    modified_time = 0

                candidate_files_info.append({
                    "original_filepath": original_filepath,
                    "display_filename": display_filename_part + ext_part,
                    "sort_key_filename": sort_key_filename_part + ext_part,
                    "modified_time": modified_time
                })
        
        if not candidate_files_info:
            return [], "状态: 未找到符合所有条件的文件。"

        if sort_by_value == "filename_asc":
            candidate_files_info.sort(key=lambda x: natural_sort_key(x["sort_key_filename"]))
        elif sort_by_value == "filename_desc":
            candidate_files_info.sort(key=lambda x: natural_sort_key(x["sort_key_filename"]), reverse=True)
        elif sort_by_value == "modified_time_asc":
            candidate_files_info.sort(key=lambda x: x["modified_time"])
        elif sort_by_value == "modified_time_desc":
            candidate_files_info.sort(key=lambda x: x["modified_time"], reverse=True)
            
        return candidate_files_info, f"状态: 找到 {len(candidate_files_info)} 个符合条件的文件。"

    def execute(self, folder_path, search_marker, remove_search_marker_from_name,
                exclude_marker, index, sort_by, file_extensions):
        
        # 将 sort_by (中文标签) 转换为内部值已在 _filter_and_sort_files 中处理
        print(f"\n[按序号加载标记图像_V2_CN] 节点执行...")
        print(f"  参数: 文件夹='{folder_path}', 搜索标记='{search_marker}', 移除搜索标记={remove_search_marker_from_name}, "
              f"排除标记='{exclude_marker}', 序号={index}, 排序方式='{sort_by}', 扩展名='{file_extensions}'")

        placeholder_image_tensor = self._create_placeholder_image_tensor()

        sorted_filtered_files, status_msg = self._filter_and_sort_files(
            folder_path, search_marker, remove_search_marker_from_name,
            exclude_marker, sort_by, file_extensions
        )

        total_files = len(sorted_filtered_files)
        print(f"[按序号加载标记图像_V2_CN] {status_msg}")

        # 更新返回的 status_msg 为中文
        if "错误:" in status_msg:
            current_status_msg_cn = status_msg # 已经是中文错误了
        elif not sorted_filtered_files:
            current_status_msg_cn = "状态: 未找到符合条件的文件。"
        else:
            current_status_msg_cn = f"状态: 共找到 {total_files} 个文件。"


        if "错误:" in status_msg or not sorted_filtered_files:
            return (placeholder_image_tensor, "", total_files if total_files > 0 else 0, current_status_msg_cn)

        if index < 0 or index >= total_files:
            error_msg_cn = f"错误: 序号 {index} 超出范围 (有效范围 0 到 {total_files - 1})。"
            print(f"[按序号加载标记图像_V2_CN] {error_msg_cn}")
            return (placeholder_image_tensor, "", total_files, error_msg_cn)

        selected_file_info = sorted_filtered_files[index]
        filepath_to_load = selected_file_info["original_filepath"]
        filename_to_return = selected_file_info["display_filename"]
        
        print(f"[按序号加载标记图像_V2_CN] 正在加载序号 {index}: '{filepath_to_load}' (返回文件名: '{filename_to_return}')")
        try:
            pil_image = Image.open(filepath_to_load)
            pil_image = ImageOps.exif_transpose(pil_image)
            if pil_image.mode == 'RGBA': pil_image = pil_image.convert('RGB')
            elif pil_image.mode == 'L': pil_image = pil_image.convert('RGB')
            elif pil_image.mode == 'P': pil_image = pil_image.convert('RGB')
            elif pil_image.mode == 'CMYK': pil_image = pil_image.convert('RGB')
            if pil_image.mode != 'RGB':
                 print(f"[按序号加载标记图像_V2_CN] 警告: 图像 '{filepath_to_load}' 模式为 {pil_image.mode}，尝试转换为RGB。")
                 pil_image = pil_image.convert('RGB')

            tensor_image = pil_to_tensor(pil_image)
            success_msg_cn = f"成功加载序号 {index}: '{filename_to_return}' (共 {total_files} 个)。"
            print(f"[按序号加载标记图像_V2_CN] {success_msg_cn}")
            return (tensor_image, filename_to_return, total_files, success_msg_cn)
        except FileNotFoundError:
            error_msg_cn = f"错误: 文件未找到: '{filepath_to_load}'"
            print(f"[按序号加载标记图像_V2_CN] {error_msg_cn}")
            return (placeholder_image_tensor, filename_to_return, total_files, error_msg_cn)
        except Exception as e:
            error_msg_cn = f"错误: 加载图像 '{filepath_to_load}' 失败: {e}"
            print(f"[按序号加载标记图像_V2_CN] {error_msg_cn}")
            return (placeholder_image_tensor, filename_to_return, total_files, error_msg_cn)

# (run_standalone_test_v2 和 节点注册部分保持不变，但类名和显示名会更新)
def run_standalone_test_v2_cn():
    # ... (可以相应汉化命令行提示) ...
    print("\n--- 按序号加载标记图像_V2_CN 独立运行测试 ---")
    test_folder = input("输入测试文件夹路径: ").strip()
    if not os.path.isdir(test_folder): print("无效文件夹，测试中止。"); return
    test_search_marker = input("输入搜索标记符号 (可为空): ").strip()
    test_remove_search = input("是否移除搜索标记从文件名? (y/n, 默认y): ").strip().lower() == 'y'
    test_exclude_marker = input("输入排除标记符号 (可为空): ").strip()
    try: test_index = int(input("输入图片序号 (0-based): "))
    except ValueError: print("无效序号，测试中止。"); return
    print("可用排序选项:")
    for i, opt in enumerate(GetMarkedImageByIndexNode_V2_CN.SORT_OPTIONS_LABELS): print(f"  {i}: {opt}")
    try:
        sort_choice_idx = int(input(f"选择排序方式 (输入数字 0-{len(GetMarkedImageByIndexNode_V2_CN.SORT_OPTIONS_LABELS)-1}): "))
        if not (0 <= sort_choice_idx < len(GetMarkedImageByIndexNode_V2_CN.SORT_OPTIONS_LABELS)): raise ValueError("选择超出范围")
        test_sort_by_label = GetMarkedImageByIndexNode_V2_CN.SORT_OPTIONS_LABELS[sort_choice_idx]
    except ValueError as e: print(f"无效排序选择: {e}。使用默认。"); test_sort_by_label = GetMarkedImageByIndexNode_V2_CN.SORT_OPTIONS_LABELS[0]
    node = GetMarkedImageByIndexNode_V2_CN()
    files, msg = node._filter_and_sort_files(test_folder, test_search_marker, test_remove_search, test_exclude_marker, test_sort_by_label, "png,jpg,jpeg,webp")
    print(msg) # msg 已经是中文了
    # ... (后续独立测试逻辑可以类似地汉化和调整) ...
    input("\n按任意键退出测试...")


if __name__ == "__main__":
    run_standalone_test_v2_cn()

NODE_CLASS_MAPPINGS = {
    "GetMarkedImageByIndex_AutoData_V2_CN": GetMarkedImageByIndexNode_V2_CN
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetMarkedImageByIndex_AutoData_V2_CN": "按序号加载标记图像 V2 [自动数据]" # UI显示名称
}