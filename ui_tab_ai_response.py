# ui_tab_ai_response.py
import tkinter as tk
from tkinter import ttk, scrolledtext

def create_ui(app_instance, parent_tab):
    """
    Tạo giao diện cho Tab "Hỏi AI Cục bộ".
    app_instance: instance của lớp SimpleQuestionViewerApp.
    parent_tab: ttk.Frame là widget cha cho tab này.
    """
    ai_chat_labelframe = ttk.LabelFrame(parent_tab, text="Chat với AI Cục bộ") # Updated title
    ai_chat_labelframe.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, ipady=5)

    app_instance.ai_chat_history_text = scrolledtext.ScrolledText(
        ai_chat_labelframe, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1, font=("Arial", 10)
    )
    app_instance.ai_chat_history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    app_instance.ai_chat_history_text.tag_configure("user_label", foreground="#007bff", font=('Arial', 10, 'bold'))
    app_instance.ai_chat_history_text.tag_configure("ai_label", foreground="#28a745", font=('Arial', 10, 'bold')) 
    app_instance.ai_chat_history_text.tag_configure("user_text", foreground="#333333")
    app_instance.ai_chat_history_text.tag_configure("ai_text", foreground="#333333")
    app_instance.ai_chat_history_text.tag_configure("bold_text", font=('Arial', 10, 'bold'))
    
    initial_greeting_message = "Xin chào! Tôi là Bot API. Bạn muốn hỏi gì?"
    
    # AIChatHandler now only uses the API, so no specific local model initialization messages from it.
    # We can directly add the greeting.
    if hasattr(app_instance, 'ai_chat_handler'):
        # Use "api_chat_bot" or "system_info" for the initial greeting.
        # "api_chat_bot" makes more sense if the bot itself is greeting.
        app_instance.ai_chat_handler.add_to_chat_history(initial_greeting_message, "api_chat_bot")
    else: 
        # Fallback if handler isn't ready (should not happen in normal flow if app_gui initializes handlers before UI tabs)
        app_instance.ai_chat_history_text.config(state=tk.NORMAL)
        app_instance.ai_chat_history_text.insert(tk.END, f"Bot (API): {initial_greeting_message}\n\n", "ai_label") # Fallback prefix
        app_instance.ai_chat_history_text.insert(tk.END, "Hệ thống: AI Chat Handler chưa được khởi tạo đúng cách.\n\n", "ai_label")
        app_instance.ai_chat_history_text.config(state=tk.DISABLED)

    chat_input_frame = ttk.Frame(ai_chat_labelframe)
    chat_input_frame.pack(fill=tk.X, padx=10, pady=(0,10))

    # --- Model Selection Combobox ---
    model_select_frame = ttk.Frame(chat_input_frame)
    model_select_frame.pack(side=tk.LEFT, padx=(0,10))

    ttk.Label(model_select_frame, text="Chọn Model:").pack(side=tk.LEFT, padx=(0, 5))

    app_instance.ai_model_select_combobox = ttk.Combobox(
        model_select_frame, 
        state="readonly", 
        width=20, # Điều chỉnh độ rộng nếu cần
        font=("Arial", 10)
    )
    if hasattr(app_instance, 'ai_chat_handler') and hasattr(app_instance.ai_chat_handler, 'AVAILABLE_AI_MODELS'):
        app_instance.ai_model_select_combobox['values'] = app_instance.ai_chat_handler.AVAILABLE_AI_MODELS
        app_instance.ai_model_select_combobox.set(app_instance.ai_chat_handler.selected_ai_model)
        app_instance.ai_model_select_combobox.bind(
            "<<ComboboxSelected>>", 
            lambda event: app_instance.ai_chat_handler.set_selected_model(app_instance.ai_model_select_combobox.get())
        )
    app_instance.ai_model_select_combobox.pack(side=tk.LEFT)
    
    app_instance.ai_chat_entry = ttk.Entry(chat_input_frame, width=60, font=("Arial", 10))
    app_instance.ai_chat_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
    
    app_instance.ai_chat_send_button = ttk.Button(
        chat_input_frame, text="Gửi", command=app_instance.send_to_ai 
    )
    app_instance.ai_chat_send_button.pack(side=tk.LEFT)
    app_instance.ai_chat_entry.bind("<Return>", lambda event: app_instance.send_to_ai())
