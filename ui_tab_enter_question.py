# ui_tab_enter_question.py
import tkinter as tk
from tkinter import ttk, scrolledtext

def create_ui(app_instance, parent_tab):
    """
    Tạo giao diện cho Tab "Nhập câu hỏi".
    app_instance: instance của lớp SimpleQuestionViewerApp.
    parent_tab: ttk.Frame là widget cha cho tab này.
    """
    local_search_labelframe = ttk.LabelFrame(parent_tab, text="Nhập câu hỏi hoặc từ khóa để tìm kiếm trong dữ liệu")
    local_search_labelframe.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, ipady=5)

    search_input_frame = ttk.Frame(local_search_labelframe)
    search_input_frame.pack(fill=tk.X, padx=10, pady=5)
    ttk.Label(search_input_frame, text="Nhập tại đây:").pack(side=tk.LEFT, padx=(0,5))
    
    app_instance.local_search_entry = ttk.Entry(search_input_frame, width=50, font=("Arial", 10))
    app_instance.local_search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
    
    app_instance.local_search_button = ttk.Button(
        search_input_frame, text="Tìm kiếm", command=app_instance.perform_local_search
    )
    app_instance.local_search_button.pack(side=tk.LEFT)
    app_instance.local_search_entry.bind("<Return>", lambda event: app_instance.perform_local_search())

    app_instance.local_search_results_text = scrolledtext.ScrolledText(
        local_search_labelframe, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1, font=("Arial", 10)
    )
    app_instance.local_search_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
    app_instance.local_search_results_text.config(state=tk.DISABLED)
    app_instance.local_search_results_text.tag_configure("header_bold", font=('Arial', 10, 'bold'))