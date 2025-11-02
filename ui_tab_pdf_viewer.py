# e:\lifetex\DHVB\ui_tab_pdf_viewer.py
import tkinter as tk
from tkinter import ttk, scrolledtext # Thêm scrolledtext

def create_ui(app_instance, parent_tab):
    """
    Tạo giao diện cho Tab "Xử lý PDF".
    app_instance: instance của lớp SimpleQuestionViewerApp.
    parent_tab: ttk.Frame là widget cha cho tab này.
    """
    # Frame chính cho tab
    main_frame = ttk.Frame(parent_tab, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Frame cho nút mở file và label
    top_frame = ttk.Frame(main_frame)
    top_frame.pack(fill=tk.X, pady=(0, 10))

    app_instance.pdf_viewer_open_button = ttk.Button(top_frame, text="Mở File PDF...", command=app_instance.pdf_viewer_open_file)
    app_instance.pdf_viewer_open_button.pack(side=tk.LEFT, padx=(0, 10))

    app_instance.pdf_viewer_current_file_label = ttk.Label(top_frame, text="Chưa có file nào được mở.")
    app_instance.pdf_viewer_current_file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # --- Khu vực OCR ---
    # Frame chính cho OCR sẽ chiếm toàn bộ không gian còn lại
    ocr_main_frame = ttk.Frame(main_frame)
    ocr_main_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    ocr_results_frame = ttk.LabelFrame(ocr_main_frame, text="Kết quả Trích xuất Văn bản từ PDF (OCR)")
    ocr_results_frame.pack(fill=tk.BOTH, expand=True)

    ocr_action_frame = ttk.Frame(ocr_results_frame)
    ocr_action_frame.pack(fill=tk.X, padx=5, pady=5)

    app_instance.pdf_viewer_extract_button = ttk.Button(
        ocr_action_frame, text="Trích xuất toàn bộ văn bản PDF (OCR)", # Đổi tên nút
        command=app_instance.pdf_viewer_extract_text_ocr # Phương thức này sẽ được tạo trong app_gui.py
    )
    app_instance.pdf_viewer_extract_button.pack(side=tk.LEFT, padx=(0, 10))
    
    app_instance.pdf_viewer_ocr_status_label = ttk.Label(ocr_action_frame, text="Trạng thái OCR: Sẵn sàng.")
    app_instance.pdf_viewer_ocr_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    app_instance.pdf_viewer_extracted_text_widget = scrolledtext.ScrolledText(
        ocr_results_frame, wrap=tk.WORD, height=8, relief=tk.SOLID, borderwidth=1, font=("Arial", 10)
    )
    app_instance.pdf_viewer_extracted_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
    app_instance.pdf_viewer_extracted_text_widget.config(state=tk.DISABLED)
