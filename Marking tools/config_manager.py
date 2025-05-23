# image_marker_tool/config_manager.py
import json
import os
from PyQt5.QtWidgets import QMessageBox # 用于显示错误

APP_SETTINGS_FILE = 'app_settings_v_pyqt.json'
SHORTCUT_CONFIG_FILE = 'marker_shortcuts_v_pyqt.json'

DEFAULT_APP_SETTINGS = {
    "play_feedback_sound": False,
    "sound_file_path": "resources/feedback.wav", # 示例
    "play_flash_feedback": False,
    "flash_color": "rgba(100, 200, 100, 100)", #淡绿色半透明
    "flash_duration_ms": 70,
    "mark_next_delay_ms": 300,
    "num_shortcuts_to_display": 10,
    "initial_window_geometry": None, # 例如 [100, 100, 1350, 900] (x, y, width, height)
    "image_extensions": "png,jpg,jpeg,webp,bmp",
    "last_opened_folder": ""
}

DEFAULT_SHORTCUT_CONFIGS = [{"prefix": "", "suffix": ""} for _ in range(10)] # 10个空配置

def load_app_settings():
    if os.path.exists(APP_SETTINGS_FILE):
        try:
            with open(APP_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # 合并加载的设置和默认设置，以确保所有键都存在
                # 加载的设置会覆盖默认值
                merged_settings = DEFAULT_APP_SETTINGS.copy()
                merged_settings.update(settings)
                return merged_settings
        except Exception as e:
            print(f"错误: 加载应用设置 '{APP_SETTINGS_FILE}' 失败: {e}")
            # QMessageBox.warning(None, "配置错误", f"加载应用设置失败: {e}\n将使用默认设置。") # 在主窗口创建前调用可能导致问题
    return DEFAULT_APP_SETTINGS.copy() # 返回默认值的副本

def save_app_settings(settings_dict, parent_widget=None):
    try:
        with open(APP_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=4, ensure_ascii=False)
        print(f"应用设置已保存到 '{APP_SETTINGS_FILE}'。")
        return True
    except Exception as e:
        print(f"错误: 保存应用设置失败: {e}")
        if parent_widget: # 只有在有父窗口时才显示消息框
            QMessageBox.critical(parent_widget, "保存错误", f"保存应用设置失败: {e}")
        return False

def load_shortcut_configs():
    if os.path.exists(SHORTCUT_CONFIG_FILE):
        try:
            with open(SHORTCUT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                shortcuts = json.load(f)
                # 确保至少有10个条目，不足则用默认空配置填充
                while len(shortcuts) < 10:
                    shortcuts.append({"prefix": "", "suffix": ""})
                return shortcuts[:10] # 只取前10个
        except Exception as e:
            print(f"错误: 加载快捷键配置 '{SHORTCUT_CONFIG_FILE}' 失败: {e}")
            # QMessageBox.warning(None, "配置错误", f"加载快捷键配置失败: {e}\n将使用默认配置。")
    return [sc.copy() for sc in DEFAULT_SHORTCUT_CONFIGS] # 返回默认值的副本列表

def save_shortcut_configs(shortcut_list, parent_widget=None):
    try:
        # 确保保存的是10个条目
        configs_to_save = shortcut_list[:10]
        while len(configs_to_save) < 10:
             configs_to_save.append({"prefix": "", "suffix": ""})

        with open(SHORTCUT_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(configs_to_save, f, indent=4, ensure_ascii=False)
        print(f"快捷键配置已保存到 '{SHORTCUT_CONFIG_FILE}'。")
        return True
    except Exception as e:
        print(f"错误: 保存快捷键配置失败: {e}")
        if parent_widget:
            QMessageBox.critical(parent_widget, "保存错误", f"保存快捷键配置失败: {e}")
        return False