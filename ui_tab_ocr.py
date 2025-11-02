# e:\lifetex\DHVB\ui_tab_ocr.py
import tkinter as tk
from tkinter import ttk, filedialog # messagebox sẽ được gọi từ handler hoặc app_instance

def create_ui(app_instance, parent_tab):
    """
    Tạo giao diện cho Tab "OCR".
    app_instance: instance của lớp SimpleQuestionViewerApp.
    parent_tab: ttk.Frame là widget cha cho tab này.
    """
    # Các biến và giá trị mặc định này sẽ được quản lý bởi OCRHandler hoặc trực tiếp trên app_instance
    # Ví dụ: app_instance.ocr_selected_image_path_var = tk.StringVar()
    #        app_instance.ocr_full_selected_image_path = ""
    #        app_instance.ocr_api_url_default = "http://192.168.0.118:5001/ocr"
    #        app_instance.ocr_json_output_dir = "json_results" # Sẽ được dùng bởi OCRHandler

    main_frame = ttk.Frame(parent_tab, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    api_url_frame = ttk.LabelFrame(main_frame, text="API Endpoint OCR")
    api_url_frame.pack(fill=tk.X, pady=5)
    ttk.Label(api_url_frame, text="URL:").pack(side=tk.LEFT, padx=5, pady=5)
    
    app_instance.ocr_api_url_entry = ttk.Entry(api_url_frame, width=50)
    app_instance.ocr_api_url_entry.insert(0, app_instance.ocr_api_url_default if hasattr(app_instance, 'ocr_api_url_default') else "http://localhost:5001/ocr")
    app_instance.ocr_api_url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

    model_frame = ttk.LabelFrame(main_frame, text="Model OCR")
    model_frame.pack(fill=tk.X, pady=5)
    ttk.Label(model_frame, text="Model (tùy chọn):").pack(side=tk.LEFT, padx=5, pady=5)
    app_instance.ocr_model_entry = ttk.Entry(model_frame, width=40)
    app_instance.ocr_model_entry.insert(0, app_instance.ocr_default_model if hasattr(app_instance, 'ocr_default_model') else "qwen2.5vl:7b")
    app_instance.ocr_model_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

    image_frame = ttk.LabelFrame(main_frame, text="Chọn Ảnh")
    image_frame.pack(fill=tk.X, pady=5)
    
    app_instance.ocr_select_image_button = ttk.Button(image_frame, text="Duyệt Ảnh...", command=app_instance.browse_image_ocr)
    app_instance.ocr_select_image_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Khởi tạo ocr_selected_image_path_var nếu chưa có
    if not hasattr(app_instance, 'ocr_selected_image_path_var'):
        app_instance.ocr_selected_image_path_var = tk.StringVar()
        app_instance.ocr_selected_image_path_var.set("Chưa chọn ảnh nào.")

    app_instance.ocr_image_path_label = ttk.Label(image_frame, textvariable=app_instance.ocr_selected_image_path_var, wraplength=350)
    app_instance.ocr_image_path_label.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

    app_instance.ocr_submit_button = ttk.Button(main_frame, text="Gọi OCR API và Lưu JSON", command=app_instance.submit_ocr_request_ocr)
    app_instance.ocr_submit_button.pack(pady=10, fill=tk.X)

    app_instance.ocr_open_search_button = ttk.Button(main_frame, text="Mở Cửa Sổ Tìm Kiếm JSON OCR", command=app_instance.open_search_window_ocr)
    app_instance.ocr_open_search_button.pack(pady=5, fill=tk.X)
    
    app_instance.ocr_status_label = ttk.Label(main_frame, text="Trạng thái OCR: Sẵn sàng", wraplength=580, relief=tk.SUNKEN, anchor=tk.W)
    app_instance.ocr_status_label.pack(pady=10, fill=tk.X, side=tk.BOTTOM)
