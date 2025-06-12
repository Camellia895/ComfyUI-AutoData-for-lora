import os
import shutil
import platform

class MigrateAndLinkFile:
    """
    一个ComfyUI节点，用于将文件迁移到新位置，并在原始位置创建符号链接或硬链接。
    - 符号链接 (Symbolic Link): 像快捷方式，可以跨磁盘，但通常没有预览图。
    - 硬链接 (Hard Link): 像文件的第二个名字，必须在同一个磁盘内，可以显示预览图。
    """
    # 节点的显示名称（中文）
    NODE_DISPLAY_NAME = "文件迁移并创建链接[自动数据]"

    @classmethod
    def INPUT_TYPES(s):
        """
        定义节点的输入参数。
        """
        return {
            "required": {
                "source_directory": ("STRING", {
                    "multiline": False,
                    "default": "D:\\ComfyUI\\output"
                }),
                "filename": ("STRING", {
                    "multiline": False,
                    "default": "ComfyUI_00001_.png"
                }),
                "destination_directory": ("STRING", {
                    "multiline": False,
                    "default": "F:\\ImageArchive"
                }),
                "link_type": (["Symbolic Link (符号链接)", "Hard Link (硬链接)"],), # <--- 新增选项
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("日志状态",)
    FUNCTION = "migrate_and_create_link"
    CATEGORY = "自动数据"

    def _get_drive(self, path):
        """辅助函数：获取路径所在的磁盘驱动器号"""
        return os.path.splitdrive(os.path.abspath(path))[0]

    def migrate_and_create_link(self, source_directory, filename, destination_directory, link_type):
        """
        执行文件迁移和创建链接的操作。
        """
        log_messages = []
        is_hard_link = (link_type == "Hard Link (硬链接)")
        
        try:
            source_path = os.path.join(source_directory, filename)
            destination_path = os.path.join(destination_directory, filename)

            log_messages.append(f"操作模式: {'硬链接 (Hard Link)' if is_hard_link else '符号链接 (Symbolic Link)'}")
            log_messages.append(f"源文件路径: {source_path}")
            log_messages.append(f"目标文件路径: {destination_path}")

            # --- 验证阶段 ---
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"错误：源文件不存在！请检查路径和文件名。路径: {source_path}")
            if os.path.isdir(source_path):
                raise IsADirectoryError(f"错误：源路径是一个文件夹，本节点只能操作文件。路径: {source_path}")
            if not os.path.isdir(destination_directory):
                log_messages.append(f"目标文件夹不存在，正在创建: {destination_directory}")
                os.makedirs(destination_directory, exist_ok=True)
            if os.path.exists(destination_path):
                raise FileExistsError(f"错误：目标位置已存在同名文件！路径: {destination_path}")

            # --- 硬链接的特定验证 ---
            if is_hard_link:
                source_drive = self._get_drive(source_path)
                dest_drive = self._get_drive(destination_path)
                log_messages.append(f"源驱动器: {source_drive}, 目标驱动器: {dest_drive}")
                if source_drive.upper() != dest_drive.upper():
                    raise ValueError(f"错误：硬链接 (Hard Link) 要求源和目标必须在同一个磁盘分区！")

            # --- 执行阶段 ---
            log_messages.append("\n步骤 1: 正在迁移文件...")
            shutil.move(source_path, destination_path)
            log_messages.append("文件迁移成功！")

            log_messages.append(f"\n步骤 2: 正在创建{'硬链接' if is_hard_link else '符号链接'}...")
            if is_hard_link:
                os.link(destination_path, source_path) # <--- 使用 os.link 创建硬链接
            else:
                os.symlink(destination_path, source_path) # <--- 使用 os.symlink 创建符号链接
            log_messages.append("链接创建成功！")
            
            log_messages.append("\n🎉 操作成功完成。")

        except Exception as e:
            error_message = f"❌ 操作失败！\n错误类型: {type(e).__name__}\n错误详情: {e}"
            if isinstance(e, OSError) and "symbolic link" in str(e).lower() and platform.system() == "Windows":
                 error_message += "\n\n**重要提示**: 创建符号链接需要管理员权限。请尝试【以管理员身份】重新启动 ComfyUI。"
            log_messages.append(error_message)

        final_log = "\n".join(log_messages)
        print(final_log)
        
        return (final_log,)

NODE_CLASS_MAPPINGS = {
    "MigrateAndLinkFile": MigrateAndLinkFile
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MigrateAndLinkFile": MigrateAndLinkFile.NODE_DISPLAY_NAME
}