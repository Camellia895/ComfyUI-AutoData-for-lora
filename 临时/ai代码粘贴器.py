import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, Listbox
import os
import datetime

class ComfyUINodeUpdaterApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("ComfyUI 节点更新工具")
        self.root.geometry("800x700")

        self.custom_nodes_dir = tk.StringVar()
        self.current_file_list = []
        self.recently_changed_files = []

        # --- 目录选择框架 ---
        dir_frame = ttk.LabelFrame(self.root, text="1. ComfyUI 自定义节点目录")
        dir_frame.pack(padx=10, pady=10, fill="x")

        ttk.Entry(dir_frame, textvariable=self.custom_nodes_dir, width=70).pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill="x")
        ttk.Button(dir_frame, text="浏览...", command=self.browse_directory).pack(side=tk.LEFT, padx=5, pady=5)

        # --- 文件管理框架 ---
        file_management_frame = ttk.Frame(self.root)
        file_management_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # 左侧面板: 现有文件
        left_pane = ttk.LabelFrame(file_management_frame, text="2. 选择现有节点或输入新文件名")
        left_pane.pack(side=tk.LEFT, padx=5, pady=5, fill="both", expand=True)

        self.filename_entry_var = tk.StringVar()
        ttk.Label(left_pane, text="文件名 (.py):").pack(anchor="w", padx=5, pady=(5,0))
        self.filename_entry = ttk.Entry(left_pane, textvariable=self.filename_entry_var, width=40)
        self.filename_entry.pack(padx=5, pady=(0,5), fill="x")
        self.filename_entry.bind("<Return>", self.apply_changes) # 允许回车保存

        ttk.Button(left_pane, text="刷新文件列表", command=self.populate_file_list).pack(pady=5, fill="x")

        list_frame = ttk.Frame(left_pane)
        list_frame.pack(fill="both", expand=True, pady=5)

        self.file_listbox = Listbox(list_frame, exportselection=False)
        self.file_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.file_listbox.config(yscrollcommand=list_scrollbar.set)


        # 右侧面板: 代码输入和最近更改
        right_pane = ttk.Frame(file_management_frame)
        right_pane.pack(side=tk.LEFT, padx=5, pady=5, fill="both", expand=True)

        code_frame = ttk.LabelFrame(right_pane, text="3. 在此处粘贴 AI 生成的代码")
        code_frame.pack(fill="both", expand=True)

        self.code_text_area = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, height=15, width=60)
        self.code_text_area.pack(padx=5, pady=5, fill="both", expand=True)

        # --- 操作框架 ---
        action_frame = ttk.LabelFrame(self.root, text="4. 操作")
        action_frame.pack(padx=10, pady=10, fill="x")

        self.apply_button = ttk.Button(action_frame, text="应用并保存更改到文件", command=self.apply_changes)
        self.apply_button.pack(pady=5)

        # --- 状态与最近更改框架 ---
        status_frame = ttk.LabelFrame(right_pane, text="最近更改/创建的文件") # 移至右侧面板
        status_frame.pack(padx=0, pady=10, fill="both", expand=False)

        self.recent_files_listbox = Listbox(status_frame, height=5)
        self.recent_files_listbox.pack(padx=5, pady=5, fill="both", expand=True)

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_label.pack(side=tk.BOTTOM, fill="x", padx=10, pady=5)
        self.status_var.set("准备就绪。请选择您的 ComfyUI custom_nodes 目录。")

        # --- 初始化 ---
        self.populate_file_list()


    def browse_directory(self):
        directory = filedialog.askdirectory(title="选择 ComfyUI 自定义节点目录")
        if directory:
            self.custom_nodes_dir.set(directory)
            self.status_var.set(f"目录已设置: {directory}")
            self.populate_file_list()
        else:
            self.status_var.set("目录选择已取消。")

    def populate_file_list(self):
        self.file_listbox.delete(0, tk.END)
        self.current_file_list = []
        directory = self.custom_nodes_dir.get()
        if directory and os.path.isdir(directory):
            try:
                for item in sorted(os.listdir(directory)):
                    if item.endswith(".py"):
                        self.file_listbox.insert(tk.END, item)
                        self.current_file_list.append(item)
                self.status_var.set(f"在 {directory} 中找到 {len(self.current_file_list)} 个 .py 文件")
            except Exception as e:
                error_msg = f"读取目录时出错: {e}"
                self.status_var.set(error_msg)
                messagebox.showerror("错误", f"无法读取目录: {directory}\n{e}")
        elif directory:
            self.status_var.set(f"目录未找到或无效: {directory}")
        else:
             self.status_var.set("请先选择您的 ComfyUI custom_nodes 目录。")


    def on_file_select(self, event=None):
        widget = event.widget if event else self.file_listbox
        selected_indices = widget.curselection()
        if selected_indices:
            selected_file = widget.get(selected_indices[0])
            self.filename_entry_var.set(selected_file)
            self.status_var.set(f"已选择现有文件: {selected_file}")
            # 可选: 加载选中文件的内容到文本区域
            # self.load_file_content(selected_file)


    # 可选: 加载文件内容函数
    def load_file_content(self, filename):
        directory = self.custom_nodes_dir.get()
        if not directory or not filename:
            return
        
        filepath = os.path.join(directory, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.code_text_area.delete('1.0', tk.END)
                    self.code_text_area.insert('1.0', f.read())
                self.status_var.set(f"已从 {filename} 加载内容")
            else:
                self.status_var.set(f"未找到文件 {filename} 以加载。")
        except Exception as e:
            error_msg = f"加载文件 {filename} 时出错: {e}"
            self.status_var.set(error_msg)
            messagebox.showerror("错误", f"无法加载文件 {filename}:\n{e}")


    def apply_changes(self, event=None):
        directory = self.custom_nodes_dir.get()
        filename_py = self.filename_entry_var.get()
        code_content = self.code_text_area.get("1.0", tk.END).strip()

        if not directory:
            messagebox.showerror("错误", "请先选择 ComfyUI custom_nodes 目录。")
            self.status_var.set("错误: ComfyUI 目录未设置。")
            return

        if not filename_py:
            messagebox.showerror("错误", "请输入或选择一个文件名 (.py)。")
            self.status_var.set("错误: 未提供文件名。")
            return

        if not filename_py.endswith(".py"):
            filename_py += ".py"
            self.filename_entry_var.set(filename_py)

        if not code_content:
            if not messagebox.askyesno("警告", "代码区域为空。您确定要保存一个空文件吗？"):
                self.status_var.set("保存已取消: 代码区域为空。")
                return

        full_path = os.path.join(directory, filename_py)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 注意：代码注释中的时间戳仍然是英文格式，这通常是代码规范的一部分。
        # 如果您也希望这些是中文，请告诉我。
        comment_start = f"# Last updated: {timestamp}"
        comment_end = f"# Updated on: {timestamp}"

        final_code = f"{comment_start}\n\n{code_content}\n\n{comment_end}\n"

        try:
            is_new_file = not os.path.exists(full_path)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(final_code)

            action = "创建" if is_new_file else "更新"
            success_msg = f"成功{action} '{filename_py}'。"
            self.status_var.set(success_msg)
            messagebox.showinfo("成功", success_msg)

            if filename_py not in self.recently_changed_files:
                self.recently_changed_files.append(filename_py)
            self.update_recent_files_listbox()

            if is_new_file and filename_py not in self.current_file_list:
                self.populate_file_list()
                if filename_py in self.current_file_list:
                    idx = self.current_file_list.index(filename_py)
                    self.file_listbox.selection_clear(0, tk.END)
                    self.file_listbox.selection_set(idx)
                    self.file_listbox.activate(idx)
                    self.file_listbox.see(idx)

        except Exception as e:
            error_msg = f"保存文件 '{filename_py}' 时出错: {e}"
            self.status_var.set(error_msg)
            messagebox.showerror("错误", error_msg)

    def update_recent_files_listbox(self):
        self.recent_files_listbox.delete(0, tk.END)
        for item in reversed(self.recently_changed_files[-10:]): # 显示最近10条
            self.recent_files_listbox.insert(tk.END, item)


if __name__ == "__main__":
    main_window = tk.Tk()
    app = ComfyUINodeUpdaterApp(main_window)
    main_window.mainloop()