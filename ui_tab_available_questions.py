# ui_tab_available_questions.py
import tkinter as tk
from tkinter import ttk, PanedWindow, scrolledtext

def create_ui(app_instance, parent_tab):
    """
    Tạo giao diện cho Tab "Danh sách câu hỏi liên quan có sẵn".
    app_instance: instance của lớp SimpleQuestionViewerApp.
    parent_tab: ttk.Frame là widget cha cho tab này.
    """
    main_container = ttk.Frame(parent_tab)
    main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    button_frame = ttk.Frame(main_container)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0), ipady=5)
    app_instance.add_questions_ai_button = ttk.Button(
        button_frame,
        text="Thêm câu hỏi mới (AI)",
        command=app_instance.generate_new_questions_with_ai # Delegates to handler
    )
    button_frame.grid_columnconfigure(0, weight=1)
    app_instance.add_questions_ai_button.grid(row=0, column=0, pady=5, sticky="ew", padx=50)
    app_instance.ai_question_status_label = ttk.Label(button_frame, text="")
    app_instance.ai_question_status_label.grid(row=1, column=0, pady=(0,5))

    tab_paned_window = PanedWindow(main_container, orient=tk.VERTICAL, sashwidth=6, background="lightgrey")
    tab_paned_window.pack(fill=tk.BOTH, expand=True)

    questions_list_pane = ttk.Frame(tab_paned_window)
    questions_list_labelframe = ttk.LabelFrame(questions_list_pane, text="Chọn câu hỏi từ danh sách")
    questions_list_labelframe.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # --- Search Frame ---
    search_frame = ttk.Frame(questions_list_labelframe)
    search_frame.pack(fill=tk.X, padx=5, pady=(5,0))
    ttk.Label(search_frame, text="Tìm câu hỏi:").pack(side=tk.LEFT, padx=(0,5))
    app_instance.available_questions_search_entry = ttk.Entry(search_frame, font=("Arial", 10))
    app_instance.available_questions_search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
    app_instance.available_questions_search_button = ttk.Button(
        search_frame,
        text="Tìm",
        command=app_instance.filter_available_questions # Delegates to handler
    )
    app_instance.available_questions_search_button.pack(side=tk.LEFT)
    app_instance.available_questions_search_entry.bind("<Return>", app_instance.filter_available_questions)
    # --- End Search Frame ---

    app_instance.available_questions_listbox = tk.Listbox(
        questions_list_labelframe, exportselection=False, activestyle='none', font=("Arial", 10), height=13 # Adjusted height
    )
    qs_scrollbar_y = ttk.Scrollbar(questions_list_labelframe, orient=tk.VERTICAL, command=app_instance.available_questions_listbox.yview)
    qs_scrollbar_x = ttk.Scrollbar(questions_list_labelframe, orient=tk.HORIZONTAL, command=app_instance.available_questions_listbox.xview)
    app_instance.available_questions_listbox.configure(yscrollcommand=qs_scrollbar_y.set, xscrollcommand=qs_scrollbar_x.set)
    qs_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    qs_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    app_instance.available_questions_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    tab_paned_window.add(questions_list_pane, minsize=150)

    # Initial population of the listbox is now handled by the filter_available_questions method
    # which is called after DataManager has populated app_instance.all_available_question_objects
    app_instance.filter_available_questions() # This will populate the listbox
    # The bind is also handled within filter_available_questions after populating

    details_display_pane = ttk.Frame(tab_paned_window)
    details_labelframe = ttk.LabelFrame(details_display_pane, text="Chi tiết câu hỏi đã chọn")
    details_labelframe.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, ipady=5)
    ttk.Label(details_labelframe, text="Câu trả lời/Mô tả chi tiết:").pack(anchor='w', padx=10, pady=(5,0))
    app_instance.available_detail_description_text = scrolledtext.ScrolledText(
        details_labelframe, height=10, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1, font=("Arial", 10)
    )
    app_instance.available_detail_description_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
    app_instance.available_detail_description_text.config(state=tk.DISABLED)
    tab_paned_window.add(details_display_pane, minsize=150)

    parent_tab.update_idletasks()
    try:
        tab_height = tab_paned_window.winfo_height()
        sash_pos_ratio = 0.58 # Adjusted due to search bar
        if tab_height > 0:
            tab_paned_window.sash_place(0, int(tab_height * sash_pos_ratio), 0)
        else:
            parent_tab.after(100, lambda: tab_paned_window.sash_place(0, int(parent_tab.winfo_height() * sash_pos_ratio), 0) if parent_tab.winfo_height() > 0 else None)
    except tk.TclError as e:
        print(f"Lưu ý: Không thể đặt vị trí thanh chia ban đầu cho Tab 1. Lỗi: {e}")

