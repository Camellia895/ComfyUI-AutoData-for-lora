import sys
import os
import json
import re # 如果清理标记逻辑需要
# from PyQt5 import QtWidgets, QtGui, QtCore # 你的PyQt5导入
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFileDialog, QMessageBox, 
                             QGraphicsScene, QGraphicsPixmapItem, QSpacerItem, QSizePolicy,)
from PyQt5.QtGui import QPixmap, QImage, QKeyEvent, QColor, QPalette
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from image_viewer import ZoomableGraphicsView # 从我们创建的文件导入
from config_manager import (load_app_settings, save_app_settings, 
                            load_shortcut_configs, save_shortcut_configs)
from settings_dialog import SettingsDialog

# from natsort import natsorted # 确保已导入
# from playsound import playsound # 确保已导入 (如果使用)

try:
    import PyQt5
    qt_plugins_path = os.path.join(PyQt5.__path__[0], "Qt5", "plugins") # 移除末尾的 "platforms" 尝试
    os.environ["QT_PLUGIN_PATH"] = qt_plugins_path # 有些系统可能认 QT_PLUGIN_PATH
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(qt_plugins_path, "platforms")
except Exception as e:
    print(f"设置PyQt5插件路径时出错 (可忽略此错误如果程序仍能运行): {e}")


from PyQt5.QtWidgets import QApplication
from main_window import ImageMarkerPyQt # 假设主窗口类在 main_window.py

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 你可以在这里设置全局样式表等
    # app.setStyleSheet("QPushButton { color: blue; }")

    window = ImageMarkerPyQt()
    
    # 从配置加载初始窗口几何位置和大小 (如果已保存)
    initial_geometry = window.app_settings.get("initial_window_geometry")
    if initial_geometry and isinstance(initial_geometry, list) and len(initial_geometry) == 4:
        try:
            window.setGeometry(*initial_geometry)
        except Exception as e:
            print(f"应用保存的窗口几何位置失败: {e}")
    else:
        window.setGeometry(100, 100, 1350, 900) # 默认大小

    window.show()
    sys.exit(app.exec_())