import os
import json
import torch # ComfyUI 的图像通常是 torch.Tensor

CATEGORY = "自动数据" 

class EmbedWorkflowJSONToImage:
    """
    一个 ComfyUI 节点，用于将指定的 .json 工作流文件内容作为元数据嵌入到图像中。
    如果图像已包含工作流元数据，则会先删除旧的，再导入新的。
    """
    
    @classmethod
    def IS_CHANGED(s, images, workflow_folder_path, workflow_file_name):
        # 强制节点重新执行，如果输入图像变化，或JSON文件路径/内容变化
        safe_file_name = "".join(c for c in workflow_file_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if not safe_file_name: safe_file_name = "workflow_data"
        if not safe_file_name.lower().endswith(".json"):
            safe_file_name += ".json" # 确保文件名包含扩展名
        
        full_json_path = os.path.join(workflow_folder_path, safe_file_name)

        json_mod_time = "no_file"
        if os.path.exists(full_json_path):
            json_mod_time = str(os.path.getmtime(full_json_path))

        # 返回组合的字符串，任何变化都将触发重新执行
        return f"{json_mod_time}_{workflow_folder_path}_{workflow_file_name}"


    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ), # 接收图像批次作为输入
                "workflow_folder_path": ("STRING", {"default": os.path.join(os.getcwd(), "workflows")}),
                "workflow_file_name": ("STRING", {"default": "my_workflow.json"}), # 默认值包含.json
            },
            "optional": {
                # 可以选择性地接收JSON数据，但默认不显示
                # 优先级高于从文件读取
                "input_workflow_data": ("JSON", {"default": "null", "hidden": True}), 
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING") 
    RETURN_NAMES = ("输出图像", "操作状态") 

    FUNCTION = "embed_data_to_image" 

    def embed_data_to_image(self, images: torch.Tensor, workflow_folder_path: str, workflow_file_name: str, input_workflow_data=None):
        workflow_data = None
        status_message = ""
        full_json_path = ""
        
        try:
            # 优先使用input_workflow_data，如果连接了外部JSON数据
            if input_workflow_data and input_workflow_data != "null":
                try:
                    workflow_data = json.loads(input_workflow_data)
                    status_message = "成功使用输入JSON数据嵌入。"
                except json.JSONDecodeError as e:
                    status_message = f"错误: 无法解析输入JSON数据: {e}"
                    return (images, status_message)
            else:
                # 1. 构建完整的JSON文件路径
                safe_file_name = "".join(c for c in workflow_file_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
                if not safe_file_name: safe_file_name = "my_workflow"
                
                # 确保文件以 .json 结尾
                if not safe_file_name.lower().endswith(".json"):
                    safe_file_name += ".json"
                    
                full_json_path = os.path.join(workflow_folder_path, safe_file_name)

                if not os.path.exists(full_json_path):
                    status_message = f"错误: 工作流JSON文件不存在: '{full_json_path}'"
                    return (images, status_message)
                
                # 2. 读取JSON文件内容
                with open(full_json_path, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                
                status_message = f"成功将工作流 '{safe_file_name}' 嵌入到图片元数据中。"

            # 3. 将工作流数据附加到每个图像的元数据中
            for i in range(images.shape[0]):
                # 确保图像 Tensor 有 .meta 属性，如果不存在则初始化
                if not hasattr(images[i], 'meta'):
                    images[i].meta = {}
                
                # --- 新增的逻辑：如果已存在“workflow”元数据，先删除它 ---
                if "workflow" in images[i].meta:
                    del images[i].meta["workflow"]
                    # status_message += " (已删除原有工作流元数据)" # 如果需要更详细的状态，可以添加此行

                images[i].meta["workflow"] = workflow_data # 导入新的工作流数据
            
            return (images, status_message)

        except FileNotFoundError:
            status_message = f"错误: 工作流JSON文件不存在: '{full_json_path}'"
        except json.JSONDecodeError as e:
            status_message = f"错误: 无法解析JSON文件 '{full_json_path}': {e}"
        except Exception as e:
            status_message = f"发生未知错误: {e}"
            print(f"Error embedding workflow JSON to image: {e}")
        
        # 发生错误时，返回原始图像和错误消息
        return (images, status_message)

NODE_CLASS_MAPPINGS = {
    "EmbedWorkflowJSONToImage": EmbedWorkflowJSONToImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EmbedWorkflowJSONToImage": "将工作流JSON嵌入图片[自动数据]"
}