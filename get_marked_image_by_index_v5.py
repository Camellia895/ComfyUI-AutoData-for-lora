# ComfyUI-AutoData-for-lora/get_marked_image_by_index_v5.py
import os
import re
import json
import time
import datetime
from PIL import Image, ImageOps
import torch
import numpy as np
from typing import List, Dict, Any, Tuple

# --- 辅助函数 ---

def _自然排序键(s: str, _nsre=re.compile('([0-9]+)')) -> List[Any]:
    return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]

# --- 主节点类 ---

class 按序号加载标记图像_V5:
    """
    按序号加载标记图像 V5 - 解决了缓存和内存泄漏问题。
    实时扫描文件夹，加载图像并输出包含文件信息和嵌入提示的完整JSON元数据。
    每次运行都会强制刷新，并确保内存被妥善释放。
    """
    
    排序选项值 = ["文件名_升序", "文件名_降序", "修改时间_升序", "修改时间_降序"]
    排序选项标签 = ["文件名 (A-Z, 0-9)", "文件名 (Z-A, 9-0)", "修改时间 (旧->新)", "修改时间 (新->旧)"]
    节点名称 = "按序号加载标记图像_V5"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文件夹路径": ("STRING", {"default": "请填入文件夹路径"}),
                "序号": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "排序方式": (cls.排序选项标签, {"default": cls.排序选项标签[0]}),
                "文件扩展名": ("STRING", {"default": "png,jpg,jpeg,webp", "placeholder": "英文逗号分隔"}),
                "搜索标记": ("STRING", {"default": "", "multiline": False}),
                "排除标记": ("STRING", {"default": "", "multiline": False}),
                "从名称中移除搜索标记": ("BOOLEAN", {"default": True, "label_on": "是", "label_off": "否"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("图像", "文件名", "元数据 (JSON)", "文件总数", "状态信息")
    FUNCTION = "加载图像"
    CATEGORY = "自动数据"
    
    # [新增] 强制刷新机制，解决缓存问题
    def IS_CHANGED(self, **kwargs):
        # 每次都返回当前时间戳，告诉ComfyUI此节点的结果总是“已更改”
        return time.time()

    def _创建占位图像(self, 宽度: int = 64, 高度: int = 64) -> torch.Tensor:
        pil_图像 = Image.new('RGB', (宽度, 高度), 'black')
        图像_np = np.array(pil_图像).astype(np.float32) / 255.0
        张量 = torch.from_numpy(图像_np).unsqueeze(0)
        pil_图像.close()
        return 张量

    def _筛选并排序文件(self, 文件夹路径: str, 搜索标记: str, 排除标记: str, 排序方式标签: str, 扩展名字符串: str) -> Tuple[List[Dict[str, Any]], str]:
        if not 文件夹路径 or not os.path.isdir(文件夹路径):
            return [], "错误: 文件夹路径无效或未指定。"
        
        有效扩展名集合 = {f".{ext.strip().lower()}" for ext in 扩展名字符串.split(',') if ext.strip()}
        if not 有效扩展名集合:
            return [], "错误: 未提供有效的文件扩展名。"

        try:
            排序方式值 = self.排序选项值[self.排序选项标签.index(排序方式标签)]
        except ValueError:
            排序方式值 = self.排序选项值[0]
            print(f"[{self.节点名称}] 警告: 无效排序标签, 使用默认 '{排序方式值}'")

        候选文件信息列表 = []
        for 文件名_带扩展名 in os.listdir(文件夹路径):
            文件基础名, 扩展名 = os.path.splitext(文件名_带扩展名)
            
            if 扩展名.lower() not in 有效扩展名集合: continue
            if 搜索标记 and 搜索标记 not in 文件基础名: continue 
            if 排除标记 and 排除标记 in 文件基础名: continue 
            
            完整路径 = os.path.join(文件夹路径, 文件名_带扩展名)
            if not os.path.isfile(完整路径): continue

            try:
                修改时间 = os.path.getmtime(完整路径)
            except OSError:
                修改时间 = 0

            候选文件信息列表.append({"完整路径": 完整路径, "文件名": 文件名_带扩展名, "修改时间": 修改时间})
        
        if not 候选文件信息列表:
            return [], "状态: 未找到符合所有条件的文件。"

        if "文件名" in 排序方式值:
            候选文件信息列表.sort(key=lambda x: _自然排序键(x["文件名"]), reverse=("降序" in 排序方式值))
        elif "修改时间" in 排序方式值:
            候选文件信息列表.sort(key=lambda x: x["修改时间"], reverse=("降序" in 排序方式值))
            
        return 候选文件信息列表, f"状态: 找到 {len(候选文件信息列表)} 个文件。"

    def _格式化文件大小(self, size_bytes: int) -> str:
        if size_bytes > 1024 * 1024: return f"{size_bytes / (1024 * 1024):.2f} MB"
        if size_bytes > 1024: return f"{size_bytes / 1024:.2f} KB"
        return f"{size_bytes} B"

    def 加载图像(self, **kwargs):
        文件夹路径 = kwargs.get("文件夹路径")
        序号 = kwargs.get("序号")
        排序方式 = kwargs.get("排序方式")
        文件扩展名 = kwargs.get("文件扩展名")
        搜索标记 = kwargs.get("搜索标记")
        排除标记 = kwargs.get("排除标记")
        从名称中移除搜索标记 = kwargs.get("从名称中移除搜索标记")

        print(f"\n[{self.节点名称}] 节点开始实时执行...")
        
        已排序文件列表, 状态消息 = self._筛选并排序文件(文件夹路径, 搜索标记, 排除标记, 排序方式, 文件扩展名)
        文件总数 = len(已排序文件列表)
        print(f"[{self.节点名称}] {状态消息}")

        if "错误:" in 状态消息 or not 已排序文件列表:
            return (self._创建占位图像(), "", "", 0, 状态消息)

        if not (0 <= 序号 < 文件总数):
            错误消息 = f"错误: 序号 {序号} 超出范围 (0 到 {文件总数 - 1})。"
            print(f"[{self.节点名称}] {错误消息}")
            return (self._创建占位图像(), "", "", 文件总数, 错误消息)

        选中的文件信息 = 已排序文件列表[序号]
        待加载的完整路径 = 选中的文件信息["完整路径"]
        待返回的文件名 = 选中的文件信息["文件名"]
        
        if 从名称中移除搜索标记 and 搜索标记:
            待返回的文件名 = 待返回的文件名.replace(搜索标记, "")
        
        pil_图像 = None # [新] 在try块外初始化，确保finally块能访问
        try:
            print(f"[{self.节点名称}] 正在加载序号 {序号}: '{待加载的完整路径}'")
            pil_图像 = Image.open(待加载的完整路径)
            pil_图像 = ImageOps.exif_transpose(pil_图像)

            fileinfo = {
                "filename": 待加载的完整路径,
                "resolution": f"{pil_图像.width}x{pil_图像.height}",
                "date": datetime.datetime.fromtimestamp(os.path.getmtime(待加载的完整路径)).strftime("%Y-%m-%d %H:%M:%S"),
                "size": self._格式化文件大小(os.path.getsize(待加载的完整路径))
            }

            embedded_params = pil_图像.info.get('parameters', pil_图像.info.get('prompt', ''))
            full_metadata = {"fileinfo": fileinfo, "parameters": embedded_params}
            metadata_json_str = json.dumps(full_metadata, ensure_ascii=False, indent=4)
            
            if pil_图像.mode != 'RGB':
                pil_图像 = pil_图像.convert('RGB')

            # --- 图像转 Tensor ---
            图像_np = np.array(pil_图像).astype(np.float32) / 255.0
            if 图像_np.ndim == 2: 图像_np = np.expand_dims(图像_np, axis=2)
            if 图像_np.shape[2] == 1: 图像_np = 图像_np.repeat(3, axis=2)
            if 图像_np.shape[2] == 4: 图像_np = 图像_np[:, :, :3]
            图像张量 = torch.from_numpy(图像_np).unsqueeze(0)
            
            成功消息 = f"成功加载序号 {序号}: '{待返回的文件名}' (共 {文件总数} 个)。"
            print(f"[{self.节点名称}] {成功消息}")
            
            return (图像张量, 待返回的文件名, metadata_json_str, 文件总数, 成功消息)
            
        except Exception as e:
            错误消息 = f"错误: 加载图像 '{待加载的完整路径}' 失败: {e}"
            print(f"[{self.节点名称}] {错误消息}")
            return (self._创建占位图像(), 待返回的文件名, "", 文件总数, 错误消息)
        
        finally:
            # [新] 严格的内存清理
            if pil_图像:
                pil_图像.close()
                print(f"[{self.节点名称}] 资源已释放: {os.path.basename(待加载的完整路径)}")
            
            # 辅助垃圾回收
            if '图像_np' in locals(): del 图像_np
            if '已排序文件列表' in locals(): del 已排序文件列表
            if '选中的文件信息' in locals(): del 选中的文件信息

# --- 节点注册 ---
NODE_CLASS_MAPPINGS = {
    "GetMarkedImageByIndex_AutoData_V5_CN": 按序号加载标记图像_V5
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetMarkedImageByIndex_AutoData_V5_CN": "按序号加载标记图像 V5 [自动数据]"
}