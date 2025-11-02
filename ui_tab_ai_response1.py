# ui_tab_ai_response1.py
import tkinter as tk
from tkinter import ttk, scrolledtext

def create_ui(app_instance, parent_tab):
    """
    Tạo giao diện cho Tab "Dựa vào AI để trả lời câu hỏi liên quan".
    app_instance: instance của lớp SimpleQuestionViewerApp.
    parent_tab: ttk.Frame là widget cha cho tab này.
    """
    ai_chat_labelframe = ttk.LabelFrame(parent_tab, text="Chat với AI để nhận câu trả lời")
    ai_chat_labelframe.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, ipady=5)

    app_instance.ai_chat_history_text = scrolledtext.ScrolledText(
        ai_chat_labelframe, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1, font=("Arial", 10)
    )
    app_instance.ai_chat_history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    app_instance.ai_chat_history_text.tag_configure("user_label", foreground="#007bff", font=('Arial', 10, 'bold'))
    app_instance.ai_chat_history_text.tag_configure("ai_label", foreground="#28a745", font=('Arial', 10, 'bold'))
    app_instance.ai_chat_history_text.tag_configure("user_text", foreground="#333333")
    app_instance.ai_chat_history_text.tag_configure("ai_text", foreground="#333333")
    # THÊM TAG MỚI CHO CHỮ ĐẬM
    app_instance.ai_chat_history_text.tag_configure("bold_text", font=('Arial', 10, 'bold'))
    
    initial_ai_message = "Xin chào! Bạn muốn hỏi gì?"
    # Check AI model status via the ai_service instance
    # Note: The provided ui_tab_ai_response.py still checks app_instance.ai_service.gemini_model
    # If you have fully switched to local transformers, this check might need adjustment
    # or rely on AIChatHandler to post status.
    # For now, keeping the Gemini check as per the provided file.
    if hasattr(app_instance.ai_service, 'gemini_model') and not app_instance.ai_service.gemini_model:
        if not (hasattr(app_instance, 'qa_pipeline') and app_instance.qa_pipeline and app_instance.is_pipeline_ready): # Check if local QA is also not ready
            initial_ai_message += "\n(Lưu ý: Kết nối AI chưa thành công và mô hình QA cục bộ có thể chưa sẵn sàng.)"
    
    # Call the handler method to add the initial message
    # The handler will now parse this message for bolding if it contains asterisks.
    app_instance.ai_chat_handler.add_to_chat_history(initial_ai_message, "ai") # Using "ai" sender type for initial message

    chat_input_frame = ttk.Frame(ai_chat_labelframe)
    chat_input_frame.pack(fill=tk.X, padx=10, pady=(0,10))
    
    app_instance.ai_chat_entry = ttk.Entry(chat_input_frame, width=60, font=("Arial", 10))
    app_instance.ai_chat_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
    
    app_instance.ai_chat_send_button = ttk.Button(
        chat_input_frame, text="Gửi", command=app_instance.send_to_ai # Delegates to handler
    )
    app_instance.ai_chat_send_button.pack(side=tk.LEFT)
    app_instance.ai_chat_entry.bind("<Return>", lambda event: app_instance.send_to_ai()) # Delegates to handler
