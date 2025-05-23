# image_marker_tool/main_window.py
import sys
import os
# import json # config_manager 会处理 json
# import re   # 如果 natural_sort_key 需要 re，但 natsort 通常更好
# import time # 主要用于 QTimer

try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                                 QLabel, QLineEdit, QFileDialog, QMessageBox,
                                 QGraphicsScene, QGraphicsPixmapItem, QSizePolicy,QScrollArea) # QScrollArea 不再需要
    from PyQt5.QtGui import QPixmap, QPalette,QImage, QColor,QKeyEvent # QPainter, QTransform, QWheelEvent, QMouseEvent 已移到 image_viewer
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal , QRectF, QPointF #已移到 image_viewer
except ImportError:
    print("错误：main_window.py - PyQt5 未正确导入。")
    raise # 或者 sys.exit(1)

# 从同级目录导入我们自定义的模块
from image_viewer import ZoomableGraphicsView
from config_manager import (load_app_settings, save_app_settings,
                            load_shortcut_configs, save_shortcut_configs)
from settings_dialog import SettingsDialog # 导入，即使我们暂时不完全使用它

try:
    from natsort import natsorted
except ImportError:
    def natsorted(seq): print("警告: natsort未安装, 文件排序可能不自然。"); return sorted(seq)

# playsound 导入现在移到使用它的方法内部，并有错误处理
# SUPPORTED_FORMATS 和配置文件名现在由 config_manager 或主应用管理

class ImageMarkerPyQt(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图像标记工具 V-PyQt")
        # self.setGeometry(100, 100, 1200, 800) # 初始几何位置在 main.py 中处理

        self.image_folder = ''
        self.image_list = [] # 将存储元组 (filename, full_filepath)
        self.current_index = -1 # 使用 -1 表示没有加载图片
        self.current_pixmap_item = None # QGraphicsPixmapItem for the current image

        # 从 config_manager 加载配置
        self.app_settings = load_app_settings()
        self.shortcut_configs_data = load_shortcut_configs() # 列表，包含10个快捷键配置字典
        
        self.num_shortcuts_to_display = self.app_settings.get("num_shortcuts_to_display", 10)

        self.setup_ui()
        self.update_shortcut_entries_from_data() # 用加载的配置填充UI
        
        self.setFocusPolicy(Qt.StrongFocus) # 允许主窗口接收键盘焦点
        self.setFocus() # 程序启动时尝试获取焦点

        # 加载上次打开的文件夹 (如果设置中有)
        last_folder = self.app_settings.get("last_opened_folder", "")
        if last_folder and os.path.isdir(last_folder):
            self.image_folder = last_folder
            self.load_images()
            if self.image_list: # 只有当加载到图片时才显示第一张
                self.show_image_at_index(0)


    def setup_ui(self):
        self.main_layout = QHBoxLayout(self) # 主布局

        # --- 左侧面板 ---
        self.left_panel_layout = QVBoxLayout()
        self.left_panel_widget = QWidget() # 用一个QWidget来容纳左侧所有东西
        self.left_panel_widget.setLayout(self.left_panel_layout)
        self.left_panel_widget.setFixedWidth(320) # 给左侧面板一个固定宽度

        # 文件夹和设置按钮
        folder_settings_layout = QHBoxLayout()
        self.folder_btn = QPushButton("选择文件夹")
        self.folder_btn.clicked.connect(self.select_folder)
        folder_settings_layout.addWidget(self.folder_btn)
        self.settings_btn = QPushButton("设置")
        self.settings_btn.clicked.connect(self.open_settings_dialog)
        folder_settings_layout.addWidget(self.settings_btn)
        self.left_panel_layout.addLayout(folder_settings_layout)

        self.status_label = QLabel("图片: 0 / 0")
        self.current_filename_label = QLabel("文件名: N/A")
        self.operation_label = QLabel("操作: 无") # 用于显示当前快捷键操作
        self.left_panel_layout.addWidget(self.status_label)
        self.left_panel_layout.addWidget(self.current_filename_label)
        self.left_panel_layout.addWidget(self.operation_label)

        # 快捷键配置区域 (可滚动)
        self.shortcut_config_scroll = QScrollArea()
        self.shortcut_config_widget = QWidget()
        self.shortcut_config_layout = QVBoxLayout(self.shortcut_config_widget)
        self.shortcut_config_scroll.setWidget(self.shortcut_config_widget)
        self.shortcut_config_scroll.setWidgetResizable(True)
        self.shortcut_config_scroll.setMinimumHeight(300) # 给一个最小高度

        self.shortcut_entry_widgets = [] # 存储 (QLabel_key, QLineEdit_prefix, QLineEdit_suffix)
        self.redraw_shortcut_config_ui() # 创建初始的快捷键配置UI

        self.left_panel_layout.addWidget(QLabel("快捷键配置:"))
        self.left_panel_layout.addWidget(self.shortcut_config_scroll)

        self.save_shortcuts_btn = QPushButton("保存快捷键配置")
        self.save_shortcuts_btn.clicked.connect(self.save_shortcut_configs_from_ui)
        self.left_panel_layout.addWidget(self.save_shortcuts_btn)
        
        self.left_panel_layout.addStretch(1) # 占位符，将按钮推到底部 (如果需要)

        # 翻页按钮
        navigation_layout = QHBoxLayout()
        self.prev_btn = QPushButton("上一张 (A)")
        self.next_btn = QPushButton("下一张 (D)")
        self.prev_btn.clicked.connect(self.show_prev_image)
        self.next_btn.clicked.connect(self.show_next_image)
        navigation_layout.addWidget(self.prev_btn)
        navigation_layout.addWidget(self.next_btn)
        self.left_panel_layout.addLayout(navigation_layout)
        
        self.main_layout.addWidget(self.left_panel_widget) # 将左侧面板添加到主布局

        # --- 右侧图片显示 (使用 QGraphicsView) ---
        self.scene = QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene, self) # 使用自定义的View
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.view, 1) # 数字1表示拉伸因子，使其占据更多空间

        self.setLayout(self.main_layout)
    def clear_layout(self, layout):
        """辅助函数：清空一个布局中的所有项目和部件"""
        if layout is not None:
            while layout.count(): # 当布局中还有项目时
                item = layout.takeAt(0) # 取出第一个项目
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None) # 解除父子关系
                    widget.deleteLater()   # 安全地删除部件
                else: # 如果项目是另一个布局
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self.clear_layout(sub_layout) # 递归清空子布局
                        # QLayouts 自身也需要被删除，但通常它们会随父部件一起被管理
                        # sub_layout.deleteLater() # 可能不需要，取决于Qt的内存管理
                        

    def redraw_shortcut_config_ui(self):
        """根据 num_shortcuts_to_display 重建快捷键配置UI"""
        # 清空旧的
        for i in reversed(range(self.shortcut_config_layout.count())): 
            widget_to_remove = self.shortcut_config_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        self.shortcut_entry_widgets = []

        self.num_shortcuts_to_display = self.app_settings.get("num_shortcuts_to_display", 10)

        for i in range(self.num_shortcuts_to_display):
            row_layout = QHBoxLayout()
            key_label_text = str((i + 1) % 10) if i < 9 else "0" # 1-9, 0
            
            key_display_label = QLabel(f"{key_label_text}:")
            prefix_label = QLabel("前缀:")
            prefix_input = QLineEdit()
            prefix_input.setPlaceholderText("可选")
            suffix_label = QLabel("后缀:")
            suffix_input = QLineEdit()
            suffix_input.setPlaceholderText("可选")

            # 为了让输入框有合理的默认宽度，可以给它们一个伸展因子或固定宽度
            # prefix_input.setFixedWidth(80)
            # suffix_input.setFixedWidth(80)

            row_layout.addWidget(key_display_label)
            row_layout.addWidget(prefix_label)
            row_layout.addWidget(prefix_input, 1) # 伸展因子
            row_layout.addWidget(suffix_label)
            row_layout.addWidget(suffix_input, 1) # 伸展因子
            
            self.shortcut_config_layout.addLayout(row_layout)
            self.shortcut_entry_widgets.append({
                "key_label": key_display_label, # 用于视觉反馈
                "prefix_edit": prefix_input,
                "suffix_edit": suffix_input
            })
        self.shortcut_config_layout.addStretch(1) # 确保条目在顶部对齐
        self.update_shortcut_entries_from_data()


    def update_shortcut_entries_from_data(self):
        """用 self.shortcut_configs_data 中的数据填充UI输入框"""
        for i in range(min(len(self.shortcut_configs_data), len(self.shortcut_entry_widgets))):
            config_data = self.shortcut_configs_data[i]
            widgets = self.shortcut_entry_widgets[i]
            widgets["prefix_edit"].setText(config_data.get("prefix", ""))
            widgets["suffix_edit"].setText(config_data.get("suffix", ""))
            # 重置背景色（如果之前有高亮）
            widgets["key_label"].setStyleSheet("") # 或设置为默认样式


    def save_shortcut_configs_from_ui(self):
        """从UI输入框收集数据并保存到 self.shortcut_configs_data 和文件"""
        # 只更新当前UI上可见的条目到 self.shortcut_configs_data
        for i in range(len(self.shortcut_entry_widgets)):
            widgets = self.shortcut_entry_widgets[i]
            if i < len(self.shortcut_configs_data): # 确保不越界
                self.shortcut_configs_data[i]["prefix"] = widgets["prefix_edit"].text().strip()
                self.shortcut_configs_data[i]["suffix"] = widgets["suffix_edit"].text().strip()
        
        if save_shortcut_configs(self.shortcut_configs_data, self): # 传递self作为父窗口给消息框
            QMessageBox.information(self, "配置", "快捷键配置已保存。")
        # (注意：save_shortcut_configs 内部已经有错误提示了)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹", self.app_settings.get("last_opened_folder", ""))
        if folder:
            self.image_folder = folder
            self.app_settings["last_opened_folder"] = folder # 保存本次选择的文件夹
            # save_app_settings(self.app_settings, self) # 可选：立即保存应用设置
            self.load_images()
            if self.image_list:
                self.show_image_at_index(0)
            else: # 清空视图如果新文件夹没有图片
                if self.current_pixmap_item: self.scene.removeItem(self.current_pixmap_item)
                self.current_pixmap_item = None
                self.update_status()


    def load_images(self):
        self.image_list = []
        if not self.image_folder or not os.path.isdir(self.image_folder):
            self.update_status()
            return

        extensions_str = self.app_settings.get("image_extensions", "png,jpg,jpeg,webp,bmp")
        valid_extensions = tuple(f".{ext.strip().lower()}" for ext in extensions_str.split(',') if ext.strip())
        
        try:
            files = os.listdir(self.image_folder)
            image_filenames = natsorted([f for f in files if os.path.splitext(f)[1].lower() in valid_extensions])
            self.image_list = [(name, os.path.join(self.image_folder, name)) for name in image_filenames]
            self.current_index = -1 # 重置索引，将在show_image_at_index中设置
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载图片列表失败: {e}")
            self.image_list = []
        self.update_status() # 更新总数等


    def show_image_at_index(self, index):
        if not self.image_list or not (0 <= index < len(self.image_list)):
            if self.current_pixmap_item:
                self.scene.removeItem(self.current_pixmap_item)
            self.current_pixmap_item = None
            self.scene.clear() # 清空场景
            self.current_index = -1
            self.update_status()
            return

        self.current_index = index
        filename, filepath = self.image_list[self.current_index]
        pixmap = QPixmap(filepath)

        if pixmap.isNull():
            QMessageBox.warning(self, "图像加载错误", f"无法加载或不支持的图像格式:\n{filepath}")
            # 从列表中移除错误图片
            self.image_list.pop(self.current_index)
            # 调整索引并尝试显示下一张或清空
            if self.image_list:
                self.current_index = min(self.current_index, len(self.image_list) - 1 if self.image_list else 0)
                if self.current_index >= 0 : self.show_image_at_index(self.current_index)
                else: self.scene.clear(); self.current_pixmap_item = None
            else:
                self.scene.clear(); self.current_pixmap_item = None
            self.update_status()
            return

        if self.current_pixmap_item:
            self.scene.removeItem(self.current_pixmap_item)
        
        self.current_pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.current_pixmap_item)
        self.scene.setSceneRect(self.current_pixmap_item.boundingRect()) # 适应新图片
        self.view.reset_zoom_and_fit(self.current_pixmap_item) # 适应视图并重置缩放
        self.update_status()


    def update_status(self):
        total = len(self.image_list)
        if total > 0 and 0 <= self.current_index < total:
            current_num = self.current_index + 1
            filename = self.image_list[self.current_index][0]
            self.status_label.setText(f"图片: {current_num} / {total}")
            self.current_filename_label.setText(f"文件名: {filename}")
        else:
            self.status_label.setText("图片: 0 / 0")
            self.current_filename_label.setText("文件名: N/A")

    def show_prev_image(self):
        if self.image_list and self.current_index > 0:
            self.show_image_at_index(self.current_index - 1)

    def show_next_image(self):
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.show_image_at_index(self.current_index + 1)
        elif self.image_list:
            # QMessageBox.information(self, "提示", "已经是最后一张图片了。") # 会打断流程
            self.operation_label.setText("提示: 已是最后一张图片。")
            self._play_sound() # 可以用不同的声音提示


    def keyPressEvent(self, event: QKeyEvent):
        # 检查焦点是否在任何快捷键配置输入框中
        is_entry_focused = False
        for widgets in self.shortcut_entry_widgets:
            if widgets["prefix_edit"].hasFocus() or widgets["suffix_edit"].hasFocus():
                is_entry_focused = True
                break
        
        if is_entry_focused:
            # 如果焦点在输入框，让输入框处理事件 (包括回车)
            # QLineEdit 的回车默认行为可能不会失去焦点，需要额外处理
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.setFocus() # 回车时将焦点移回主窗口
            else:
                super().keyPressEvent(event) # 其他键让QLineEdit自己处理
            return

        # 如果焦点不在输入框，处理全局快捷键
        key = event.key()
        processed = False

        if key == Qt.Key_A:
            self.show_prev_image()
            processed = True
        elif key == Qt.Key_D:
            self.show_next_image()
            processed = True
        elif Qt.Key_0 <= key <= Qt.Key_9:
            qt_key_to_config_index = {
                Qt.Key_1: 0, Qt.Key_2: 1, Qt.Key_3: 2, Qt.Key_4: 3, Qt.Key_5: 4,
                Qt.Key_6: 5, Qt.Key_7: 6, Qt.Key_8: 7, Qt.Key_9: 8, Qt.Key_0: 9
            }
            if key in qt_key_to_config_index:
                config_index = qt_key_to_config_index[key]
                if config_index < self.num_shortcuts_to_display: # 只处理当前UI上可见的配置
                    self.apply_tag_and_next(config_index)
                else:
                    print(f"快捷键 {key-Qt.Key_0} 对应的配置当前未显示。")
                processed = True
        
        if not processed:
            super().keyPressEvent(event)


    def apply_tag_and_next(self, config_index):
        if not self.image_list or not (0 <= self.current_index < len(self.image_list)):
            self.operation_label.setText("错误: 没有选中图片")
            return
        if not (0 <= config_index < len(self.shortcut_configs_data)):
            self.operation_label.setText(f"错误: 无效的快捷键配置索引 {config_index}")
            return

        config = self.shortcut_configs_data[config_index]
        prefix = config.get("prefix", "").strip()
        suffix = config.get("suffix", "").strip()

        if not prefix and not suffix:
            self.operation_label.setText(f"快捷键 {config_index_to_display(config_index)} 配置为空, 仅翻页")
            self._play_sound()
            self._flash_feedback()
            QTimer.singleShot(self.app_settings.get("mark_next_delay_ms", 300), self.show_next_image)
            return

        # 视觉反馈：高亮对应行
        for i, widgets in enumerate(self.shortcut_entry_widgets):
            style = "background-color: green; color: white;" if i == config_index else ""
            widgets["key_label"].setStyleSheet(style) # 高亮整行或只是标签
            # widgets["prefix_edit"].setStyleSheet(style) # 也可以高亮输入框
            # widgets["suffix_edit"].setStyleSheet(style)


        original_filename, old_path = self.image_list[self.current_index]
        name_part, ext_part = os.path.splitext(original_filename)
        
        # 清理旧标记的逻辑 (与CustomTkinter版本类似，但使用当前所有配置)
        temp_name_part = name_part
        for i_clean in range(len(self.shortcut_configs_data)): # 检查所有10个配置
            # if i_clean == config_index: continue # 不移除当前要应用的（可选）
            p_conf = self.shortcut_configs_data[i_clean]
            p_pre = p_conf.get("prefix", "").strip()
            p_suf = p_conf.get("suffix", "").strip()
            if p_suf and temp_name_part.endswith(p_suf):
                temp_name_part = temp_name_part[:-len(p_suf)]
            if p_pre and temp_name_part.startswith(p_pre):
                temp_name_part = temp_name_part[len(p_pre):]
        
        base_name = temp_name_part.strip()
        new_name_part = f"{prefix}{base_name}{suffix}"
        new_filename = new_name_part + ext_part
        new_path = os.path.join(self.image_folder, new_filename)

        op_label_text = f"标记: {config_index_to_display(config_index)} (前='{prefix}',后='{suffix}')"
        self.operation_label.setText(op_label_text)

        if new_filename == original_filename:
            print(f"文件名 '{original_filename}' 无需更改。")
        else:
            if os.path.exists(new_path):
                QMessageBox.warning(self, "重命名失败", f"目标文件已存在: {new_path}")
                self._clear_shortcut_feedback(config_index) # 清除高亮
                return
            try:
                os.rename(old_path, new_path)
                self.image_list[self.current_index] = (new_filename, new_path) # 更新内部列表
                print(f"重命名: '{original_filename}' -> '{new_filename}'")
            except Exception as e:
                QMessageBox.critical(self, "重命名错误", f"无法重命名文件:\n{old_path}\n到\n{new_path}\n错误: {e}")
                self._clear_shortcut_feedback(config_index) # 清除高亮
                return

        self._play_sound()
        self._flash_feedback()
        self.update_status() # 更新显示的文件名
        QTimer.singleShot(self.app_settings.get("mark_next_delay_ms", 300), self.show_next_image)
        QTimer.singleShot(self.app_settings.get("mark_next_delay_ms", 300) + 700, 
                          lambda ci=config_index: self._clear_shortcut_feedback(ci))


    def _clear_shortcut_feedback(self, last_config_index):
        if 0 <= last_config_index < len(self.shortcut_entry_widgets):
            widgets = self.shortcut_entry_widgets[last_config_index]
            widgets["key_label"].setStyleSheet("") # 恢复默认样式
            # widgets["prefix_edit"].setStyleSheet("")
            # widgets["suffix_edit"].setStyleSheet("")
        self.operation_label.setText("操作: 无")


    def _play_sound(self):
        if self.app_settings.get("play_feedback_sound", False) and PLAYSOUND_AVAILABLE:
            sound_file = self.app_settings.get("sound_file_path", "resources/feedback.wav")
            if os.path.exists(sound_file):
                try:
                    playsound(sound_file, block=False)
                except Exception as e:
                    print(f"播放声音文件 '{sound_file}' 失败: {e}")
            # else: print(f"声音文件未找到: {sound_file}") # 避免过多打印

    def _flash_feedback(self):
        if self.app_settings.get("play_flash_feedback", False):
            try:
                flash_color_str = self.app_settings.get("flash_color", "rgba(100, 200, 100, 100)")
                # 解析 rgba 字符串 (简单实现)
                parts = flash_color_str.replace("rgba(", "").replace(")", "").split(',')
                r, g, b, a = [int(p.strip()) for p in parts]
                
                original_palette = self.view.palette()
                flash_palette = QPalette(original_palette)
                flash_palette.setColor(QPalette.Window, QColor(r,g,b,a)) # Window role for QGraphicsView background

                self.view.setAutoFillBackground(True) # 需要设置这个才能让palette生效
                self.view.setPalette(flash_palette)
                
                flash_duration = self.app_settings.get("flash_duration_ms", 70)
                QTimer.singleShot(flash_duration, lambda: self._restore_view_palette(original_palette))
            except Exception as e:
                print(f"闪烁反馈失败: {e}")
                
    def _restore_view_palette(self, original_palette):
        if self.view and self.view.isVisible(): # 检查视图是否存在
             self.view.setPalette(original_palette)
             self.view.setAutoFillBackground(False) # 恢复默认


    def open_settings_dialog(self):
        # 创建并显示设置对话框
        # `self.app_settings` 是当前应用的设置字典
        # `self.shortcut_configs_data` 是当前快捷键配置列表
        # 对话框需要能修改 `self.app_settings` 并触发主窗口的更新
        dialog = SettingsDialog(self.app_settings.copy(), self) # 传递副本，避免直接修改
        dialog.settings_applied.connect(self.apply_settings_from_dialog)
        dialog.exec_() # 显示为模态对话框

    def apply_settings_from_dialog(self):
        # 这个槽函数由 SettingsDialog 的 settings_applied 信号触发
        # SettingsDialog 内部已经修改了传递给它的设置字典的副本
        # 我们可以从 SettingsDialog 实例获取更新后的设置（如果需要，但通常对话框直接修改副本）
        # dialog = self.sender() # 获取信号发送者，即SettingsDialog实例
        # if dialog and isinstance(dialog, SettingsDialog):
        #     updated_settings = dialog.get_settings() # 从对话框获取最终确认的设置
        #     
        #     old_num_display = self.app_settings.get("num_shortcuts_to_display", 10)
        #     
        #     self.app_settings.update(updated_settings) # 更新主应用的设置
        #     save_app_settings(self.app_settings, self) # 保存到文件
        #     
        #     new_num_display = self.app_settings.get("num_shortcuts_to_display", 10)
        #     if old_num_display != new_num_display:
        #         self.redraw_shortcut_config_ui() # 如果显示数量改变，重绘UI
        #     print("应用设置已从对话框更新并保存。")

        # 简化的方式：SettingsDialog在accept时已经修改了传给它的字典副本，
        # 并且主窗口的 self.app_settings 已经被 SettingsDialog 的 apply_and_accept 方法更新了
        # （如果 SettingsDialog 直接修改 self.master_app.config）。
        # 如果 SettingsDialog 只修改自己的副本，则需要下面的逻辑：
        
        dialog = self.sender() # 获取信号发送者，即SettingsDialog实例
        if not (dialog and isinstance(dialog, SettingsDialog)):
            return

        updated_settings = dialog.get_settings() # 从对话框获取最终确认的设置
            
        old_num_display = self.app_settings.get("num_shortcuts_to_display", 10)
        
        self.app_settings.update(updated_settings) # 更新主应用的设置
        save_app_settings(self.app_settings, self) # 保存到文件
        
        new_num_display = self.app_settings.get("num_shortcuts_to_display", 10)
        if old_num_display != new_num_display:
            # self.num_shortcuts_to_display = new_num_display # 这个变量会在redraw中更新
            self.redraw_shortcut_config_ui() 
        print("应用设置已从对话框更新并保存。")


    def closeEvent(self, event):
        """处理窗口关闭事件，保存配置"""
        # 保存应用设置（例如窗口大小和位置）
        self.app_settings["initial_window_geometry"] = [self.x(), self.y(), self.width(), self.height()]
        save_app_settings(self.app_settings, self)
        # 快捷键配置通常通过按钮保存，但也可以在这里加一个最终保存
        # save_shortcut_configs(self.shortcut_configs_data, self) 
        event.accept()

def config_index_to_display(index):
    """将0-9的内部索引转为UI上显示的1-9,0"""
    return str((index + 1) % 10) if index < 9 else "0"