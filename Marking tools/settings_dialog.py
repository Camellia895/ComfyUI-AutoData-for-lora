# image_marker_tool/settings_dialog.py
try:
    from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox,
                                 QSpinBox, QSlider, QLineEdit, QFileDialog, QColorDialog,
                                 QDialogButtonBox, QMessageBox,QSizePolicy, QFrame, QGroupBox)
    from PyQt5.QtGui import QColor, QPalette
    from PyQt5.QtCore import Qt, pyqtSignal
except ImportError:
    print("错误：settings_dialog.py - PyQt5 未安装或无法导入。")
    raise

class SettingsDialog(QDialog):
    settings_applied = pyqtSignal() # 当设置被应用时发出此信号

    def __init__(self, current_settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置与帮助")
        self.setMinimumSize(500, 600) # 设置对话框的最小尺寸
        self.settings = current_settings # 传入当前设置的副本进行编辑

        self.layout = QVBoxLayout(self)

        # --- 反馈设置 ---
        feedback_group = QGroupBox("反馈选项")
        feedback_layout = QVBoxLayout()

        self.sound_checkbox = QCheckBox("启用声音反馈 (需要playsound库)")
        self.sound_checkbox.setChecked(self.settings.get("play_feedback_sound", False))
        feedback_layout.addWidget(self.sound_checkbox)
        
        # (选择声音文件的按钮可以后续添加)
        # self.sound_file_button = QPushButton("选择声音文件...")
        # self.sound_file_label = QLabel(self.settings.get("sound_file_path", "未选择"))
        # feedback_layout.addWidget(self.sound_file_button)
        # feedback_layout.addWidget(self.sound_file_label)

        self.flash_checkbox = QCheckBox("启用图片区闪烁反馈")
        self.flash_checkbox.setChecked(self.settings.get("play_flash_feedback", False))
        feedback_layout.addWidget(self.flash_checkbox)
        
        # (选择闪烁颜色的按钮可以后续添加)
        # self.flash_color_button = QPushButton("选择闪烁颜色")
        # self.flash_color_preview = QLabel() # 用于显示颜色
        # self._update_flash_color_preview(self.settings.get("flash_color", "rgba(100,200,100,100)"))
        # feedback_layout.addWidget(self.flash_color_button)
        # feedback_layout.addWidget(self.flash_color_preview)


        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("标记后翻页延迟 (毫秒):"))
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(0, 5000) # 0到5秒
        self.delay_spinbox.setSingleStep(50)
        self.delay_spinbox.setValue(self.settings.get("mark_next_delay_ms", 300))
        delay_layout.addWidget(self.delay_spinbox)
        delay_layout.addStretch()
        feedback_layout.addLayout(delay_layout)
        feedback_group.setLayout(feedback_layout)
        self.layout.addWidget(feedback_group)

        # --- 界面设置 ---
        ui_group = QGroupBox("界面选项")
        ui_layout = QVBoxLayout()

        shortcut_num_layout = QHBoxLayout()
        shortcut_num_layout.addWidget(QLabel("显示的快捷键配置数量 (1-10):"))
        self.num_shortcuts_spinbox = QSpinBox() # 使用 SpinBox 更精确
        self.num_shortcuts_spinbox.setRange(1, 10)
        self.num_shortcuts_spinbox.setValue(self.settings.get("num_shortcuts_to_display", 10))
        shortcut_num_layout.addWidget(self.num_shortcuts_spinbox)
        shortcut_num_layout.addStretch()
        ui_layout.addLayout(shortcut_num_layout)
        
        ext_layout = QHBoxLayout()
        ext_layout.addWidget(QLabel("支持的图片后缀 (逗号分隔):"))
        self.extensions_input = QLineEdit(self.settings.get("image_extensions", "png,jpg,jpeg,webp,bmp"))
        ext_layout.addWidget(self.extensions_input)
        ui_layout.addLayout(ext_layout)
        
        # (窗口分辨率和字体大小设置较为复杂，暂时不直接加入UI，可以通过修改JSON实现)

        ui_group.setLayout(ui_layout)
        self.layout.addWidget(ui_group)

        # --- 帮助按钮 ---
        self.help_button = QPushButton("帮助 / 说明")
        self.help_button.clicked.connect(self.show_help_info)
        self.layout.addWidget(self.help_button, 0, Qt.AlignCenter) # 居中

        self.layout.addStretch() # 将按钮推到底部

        # --- 对话框按钮 ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.apply_and_accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    # def _update_flash_color_preview(self, color_str):
    #     # ... (如果添加颜色选择器，则实现此方法) ...
    #     pass

    def apply_and_accept(self):
        # 从UI控件收集设置值到 self.settings 字典
        self.settings["play_feedback_sound"] = self.sound_checkbox.isChecked()
        self.settings["play_flash_feedback"] = self.flash_checkbox.isChecked()
        self.settings["mark_next_delay_ms"] = self.delay_spinbox.value()
        self.settings["num_shortcuts_to_display"] = self.num_shortcuts_spinbox.value()
        self.settings["image_extensions"] = self.extensions_input.text().strip()
        # (其他设置...)

        self.settings_applied.emit() # 发出信号，通知主窗口设置已应用
        self.accept() # 关闭对话框并返回 QDialog.Accepted

    def get_settings(self) -> dict:
        """返回用户在对话框中确认的设置"""
        return self.settings

    def show_help_info(self):
        help_text = """图像标记工具 - 帮助说明

1.  **选择文件夹**: 点击 "选择文件夹" 按钮来加载图片。
2.  **图片浏览**: 
    - 使用键盘 "A" (上一张) / "D" (下一张) 键或对应按钮翻页。
    - 鼠标滚轮在图片上可缩放。
    - 按住鼠标左键在图片上可拖动平移。
3.  **快捷键标记 (数字0-9)**:
    - 在主界面左侧的 "快捷键标记配置" 区域，为每个数字键设置文件名前缀和后缀。
    - 按下对应的数字键，配置的标记将被应用到当前图片文件名，并自动跳转到下一张。
    - 标记逻辑: 会尝试先移除所有已配置的快捷键组合标记，再应用新标记，以避免重复。
    - **重要**: 只有当键盘焦点不在任何快捷键配置输入框中时，这些快捷键才会生效。如果在输入框中编辑，请按回车键或点击图片区域以使输入框失去焦点。
4.  **文件名修改**: 操作直接修改硬盘上的文件名。请谨慎操作，建议备份重要图片！
5.  **设置**:
    - **反馈选项**: 控制操作后的声音和图片区域闪烁提示。可调整自动翻页延迟。
    - **界面选项**: 控制主界面显示多少条快捷键配置（1-10条）。更改支持的图片后缀（英文逗号分隔）。
    - 更改设置后需点击 "应用并保存设置"。
6.  **配置文件**:
    - 应用设置保存在 `app_settings_v_pyqt.json`。
    - 快捷键配置保存在 `marker_shortcuts_v_pyqt.json`。
    - 这两个文件通常与应用程序在同一目录。

祝您使用愉快！
"""
        QMessageBox.information(self, "帮助与说明", help_text)