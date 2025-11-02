#Visualize tab
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog # Đảm bảo scrolledtext được import
import os
import json

class DocumentStatsWindow:
    def __init__(self, parent, person_name, source_filename):
        self.parent = parent
        self.person_name = person_name
        self.source_filename = source_filename
        self.json_results_dir = r"C:\Users\mduc1\OneDrive\Desktop\DHVB\DHVB\json_results"
        self.detail_json_dir = r"C:\Users\mduc1\OneDrive\Desktop\DHVB\pdf_split_json_results"
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Thống Kê Tài Liệu - {person_name}")
        self.window.geometry("1200x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_text = f"THÔNG KÊ TÀI LIỆU CÓ TRONG HỒ SƠ - {self.person_name}"
        title_label = ttk.Label(main_frame, text=title_text, 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create treeview frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Define columns
        columns = ('STT', 'Trích Yếu Tài Liệu', 'Từ Tờ Đến Tờ', 'Đặc Điểm Tài Liệu', 'Độ Mật', 'Ghi Chú')
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configure column headings and widths
        self.tree.heading('STT', text='STT')
        self.tree.heading('Trích Yếu Tài Liệu', text='Trích Yếu Tài Liệu')
        self.tree.heading('Từ Tờ Đến Tờ', text='Từ Tờ Đến Tờ')
        self.tree.heading('Đặc Điểm Tài Liệu', text='Đặc Điểm Tài Liệu')
        self.tree.heading('Độ Mật', text='Độ Mật')
        self.tree.heading('Ghi Chú', text='Ghi Chú')
        
        # Configure column widths
        self.tree.column('STT', width=50, minwidth=40)
        self.tree.column('Trích Yếu Tài Liệu', width=300, minwidth=200)
        self.tree.column('Từ Tờ Đến Tờ', width=100, minwidth=80)
        self.tree.column('Đặc Điểm Tài Liệu', width=120, minwidth=100)
        self.tree.column('Độ Mật', width=80, minwidth=60)
        self.tree.column('Ghi Chú', width=150, minwidth=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack the treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind double-click event to the treeview
        self.tree.bind('<Double-1>', self._on_document_double_click)
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Close button
        close_button = ttk.Button(main_frame, text="Đóng", command=self.window.destroy)
        close_button.pack(pady=(10, 0))

    def _on_document_double_click(self, event):
        """Handle double-click event on a document in the treeview."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return

        values = self.tree.item(item, 'values')
        if not values or len(values) < 2: # Ensure 'Trích Yếu Tài Liệu' exists
            messagebox.showwarning("Lỗi", "Không tìm thấy thông tin 'Trích Yếu Tài Liệu'.", parent=self.window)
            return

        document_title = values[1] # 'Trích Yếu Tài Liệu' column

        # Construct potential filename (assume .json extension)
        json_filename = f"{document_title}.json"
        json_filepath = os.path.join(self.detail_json_dir, json_filename)

        if not os.path.exists(json_filepath):
            messagebox.showwarning("Không tìm thấy", f"Không tìm thấy file:\n'{json_filepath}'", parent=self.window)
            return
        
        # Open a new window to display the document's content
        self._display_document_content(json_filepath, document_title)
    
    def _display_document_content(self, filepath, title):
        """Displays the extracted text content of a JSON file in a new window."""
        content_window = tk.Toplevel(self.window)
        content_window.title(f"Nội dung tài liệu - {title}")
        content_window.geometry("800x600")
        content_window.transient(self.window)
        content_window.grab_set()

        text_area = scrolledtext.ScrolledText(content_window, wrap=tk.WORD, width=90, height=30, font=("Segoe UI", 10))
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                text_content = self._extract_text_from_json(json_data)
                if not text_content:
                    text_content = f"Không tìm thấy nội dung văn bản đã xử lý hoặc OCR trong file '{os.path.basename(filepath)}'."
                text_area.insert(tk.END, text_content)
        except FileNotFoundError:
            text_area.insert(tk.END, f"Lỗi: Không tìm thấy file tại đường dẫn {filepath}")
        except json.JSONDecodeError:
            text_area.insert(tk.END, f"Lỗi: Không thể giải mã JSON từ file {filepath}. Vui lòng kiểm tra định dạng file.")
        except Exception as e:
            text_area.insert(tk.END, f"Lỗi không xác định khi đọc file {filepath}: {e}")
        
        text_area.config(state=tk.DISABLED) # Make text read-only

    def _extract_text_from_json(self, json_data):
        """
        Trích xuất văn bản từ cấu trúc JSON đã cho.
        Ưu tiên 'ai_processed_text', sau đó đến 'original_ocr_text'.
        """
        extracted_texts = []
        if isinstance(json_data, dict) and "pages" in json_data:
            for page in json_data["pages"]:
                if "ai_processed_text" in page and page["ai_processed_text"]:
                    extracted_texts.append(page["ai_processed_text"])
                elif "original_ocr_text" in page and page["original_ocr_text"]:
                    extracted_texts.append(page["original_ocr_text"])
        return "\n\n---\n\n".join(extracted_texts) # Use separators for clarity
    
    def _load_data(self):
        """Load document data from all JSON files in json_results directory"""
        try:
            if not os.path.exists(self.json_results_dir):
                messagebox.showerror("Lỗi", f"Không tìm thấy thư mục: {self.json_results_dir}", parent=self.window)
                return
            
            # Get all JSON files and sort them
            json_files = [f for f in os.listdir(self.json_results_dir) if f.endswith('.json')]
            if not json_files:
                messagebox.showerror("Lỗi", "Không tìm thấy file JSON nào trong thư mục json_results", parent=self.window)
                return
            
            # Sort files to ensure proper order (file1, file2, file3, file4)
            json_files.sort()
            
            all_documents = []
            files_loaded = []
            
            # Load data from all JSON files
            for json_file in json_files:
                json_file_path = os.path.join(self.json_results_dir, json_file)
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    danh_sach = data.get('danhSachTaiLieu', [])
                    if danh_sach:
                        all_documents.extend(danh_sach)
                        files_loaded.append(json_file)
                    
                except json.JSONDecodeError as e:
                    messagebox.showwarning("Cảnh báo", f"Lỗi đọc file {json_file}: {str(e)}", parent=self.window)
                except Exception as e:
                    messagebox.showwarning("Cảnh báo", f"Lỗi xử lý file {json_file}: {str(e)}", parent=self.window)
            
            if not all_documents:
                self.status_var.set("Không có dữ liệu tài liệu")
                messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu 'danhSachTaiLieu' trong các file JSON", parent=self.window)
                return
            
            # Display all documents with continuous numbering
            stt_counter = 1
            for item in all_documents:
                # Extract data with proper handling of None values
                trich_yeu = item.get('trichYeu', '') or ''
                so_to = item.get('soTo', '') or ''
                dac_diem = item.get('dacDiem', '') or ''
                do_mat = item.get('doMat', '') or ''
                ghi_chu = item.get('ghiChu', '') or ''
                
                # Insert into treeview
                self.tree.insert('', 'end', values=(
                    stt_counter,
                    trich_yeu,
                    so_to,
                    dac_diem,
                    do_mat,
                    ghi_chu
                ))
                
                stt_counter += 1
            
            # Update status
            self.status_var.set(f"Đã tải {len(all_documents)} bản ghi tài liệu từ {len(files_loaded)} file: {', '.join(files_loaded)}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý dữ liệu: {str(e)}", parent=self.window)
            self.status_var.set("Lỗi tải dữ liệu")

class VisualizeTab:
    def __init__(self, app_instance, parent_tab):
        self.app = app_instance
        self.parent_tab = parent_tab
        
        # Initialize ocr_json_dir to None. User will select this.
        self.ocr_json_dir = None 

        self._create_widgets()

    def _create_widgets(self):
        # Main frame for the entire Tab 6
        main_frame = ttk.Frame(self.parent_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook to organize different functionalities within Tab 6
        tab_control = ttk.Notebook(main_frame)

        # Tab 1: OCR Image (Functionality from original Tab 4)
        ocr_image_tab = ttk.Frame(tab_control)
        tab_control.add(ocr_image_tab, text="1.OCR Ảnh  ")
        self._create_ocr_image_sub_tab(ocr_image_tab)

        # Tab 2: Process PDF (Functionality from original Tab 5)
        pdf_process_tab = ttk.Frame(tab_control)
        tab_control.add(pdf_process_tab, text="2.Xử Lý & OCR PDF  ")
        self._create_pdf_processing_sub_tab(pdf_process_tab)

        # Tab 3: Visualize Data (Existing Treeview for OCR results)
        visualize_data_tab = ttk.Frame(tab_control)
        tab_control.add(visualize_data_tab, text="3.Trực Quan Hóa Dữ Liệu Phạm Nhân") # Đã cập nhật số thứ tự
        self._create_visualize_data_sub_tab(visualize_data_tab)

        tab_control.pack(expand=1, fill="both")

    def _create_ocr_image_sub_tab(self, parent_tab_frame):
        """
        Creates the UI for OCRing single images.
        Features are hidden, only "Duyệt Ảnh..." button is shown.
        OCR is triggered automatically after image selection.
        A ScrolledText widget is added to display JSON results.
        """
        ocr_frame = ttk.Frame(parent_tab_frame, padding="10")
        ocr_frame.pack(fill=tk.BOTH, expand=True)

        # --- API URL Entry (Created but not packed) ---
        api_url_frame_hidden = ttk.Frame(ocr_frame) 
        self.app.ocr_api_url_entry = ttk.Entry(api_url_frame_hidden, width=50)
        self.app.ocr_api_url_entry.insert(0, self.app.ocr_api_url_default if hasattr(self.app, 'ocr_api_url_default') else "http://localhost:5000/describe_image")

        # --- Model Entry (Created but not packed) ---
        model_frame_hidden = ttk.Frame(ocr_frame) 
        self.app.ocr_model_entry = ttk.Entry(model_frame_hidden, width=40)
        self.app.ocr_model_entry.insert(0, self.app.ocr_default_model if hasattr(self.app, 'ocr_default_model') else "qwen2.5vl:7b")

        # --- Image Selection (Visible) ---
        image_select_frame = ttk.LabelFrame(ocr_frame, text="Chọn Ảnh")
        image_select_frame.pack(fill=tk.X, pady=5, anchor='nw') 
        
        self.app.ocr_select_image_button = ttk.Button(image_select_frame, text="Duyệt Ảnh...", command=self.app.browse_image_ocr)
        self.app.ocr_select_image_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Thêm nút mới cho OCR thư mục thống kê tài liệu
        self.app.ocr_folder_stats_button = ttk.Button(
            image_select_frame, 
            text="OCR Thư mục Thống kê Tài liệu...",
            command=self.app.process_document_stats_folder_ocr 
        )
        self.app.ocr_folder_stats_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        if not hasattr(self.app, 'ocr_selected_image_path_var'): 
            self.app.ocr_selected_image_path_var = tk.StringVar()
            self.app.ocr_selected_image_path_var.set("Chưa chọn ảnh nào.")

        # --- JSON Display Area (Visible) ---
        json_display_frame = ttk.LabelFrame(ocr_frame, text="Nội dung JSON trích xuất")
        json_display_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 5))

        self.app.ocr_json_display_text = scrolledtext.ScrolledText(
            json_display_frame, 
            wrap=tk.WORD, 
            height=10, # Chiều cao có thể điều chỉnh
            font=("Courier New", 9) # Font phù hợp cho JSON
        )
        self.app.ocr_json_display_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.app.ocr_json_display_text.config(state=tk.DISABLED) # Ban đầu ở chế độ chỉ đọc
        
        # --- Status Label (Created but not packed) ---
        self.app.ocr_status_label = ttk.Label(ocr_frame, text="Trạng thái OCR: Sẵn sàng")

    def _create_pdf_processing_sub_tab(self, parent_tab_frame):
        """Creates the UI for PDF processing, similar to original Tab 5."""
        pdf_frame = ttk.Frame(parent_tab_frame, padding="10")
        pdf_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(pdf_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        self.app.pdf_viewer_open_button = ttk.Button(top_frame, text="Mở File PDF...", command=self.app.pdf_viewer_open_file)
        self.app.pdf_viewer_open_button.pack(side=tk.LEFT, padx=(0, 10))

        self.app.pdf_viewer_current_file_label = ttk.Label(top_frame, text="Chưa có file nào được mở.")
        self.app.pdf_viewer_current_file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ocr_results_frame = ttk.LabelFrame(pdf_frame, text="Kết quả Trích xuất Văn bản từ PDF (OCR)")
        ocr_results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        ocr_action_frame = ttk.Frame(ocr_results_frame)
        ocr_action_frame.pack(fill=tk.X, padx=5, pady=5)

        self.app.pdf_viewer_extract_button = ttk.Button(
            ocr_action_frame, text="Trích xuất toàn bộ văn bản PDF (OCR)",
            command=lambda: self.app.asyncio.run(self.app.pdf_viewer_extract_text_ocr()) if hasattr(self.app, "asyncio") else self.app.pdf_viewer_extract_text_ocr()
        )
        self.app.pdf_viewer_extract_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.app.pdf_viewer_ocr_status_label = ttk.Label(ocr_action_frame, text="Trạng thái OCR: Sẵn sàng.")
        self.app.pdf_viewer_ocr_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.app.pdf_viewer_extracted_text_widget = scrolledtext.ScrolledText(
            ocr_results_frame, wrap=tk.WORD, height=8, relief=tk.SOLID, borderwidth=1, font=("Arial", 10)
        )
        self.app.pdf_viewer_extracted_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        self.app.pdf_viewer_extracted_text_widget.config(state=tk.DISABLED)

    def _create_visualize_data_sub_tab(self, parent_frame_for_visualize):
        """Creates the UI for visualizing OCRed data from JSON files (original Tab 6 content)."""
        controls_frame = ttk.Frame(parent_frame_for_visualize)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        self.select_ocr_dir_button = ttk.Button(controls_frame, text="Chọn thư mục JSON OCR Ảnh...", command=self._select_ocr_json_directory)
        self.select_ocr_dir_button.pack(side=tk.LEFT, padx=(0, 10))

        self.selected_ocr_dir_label_var = tk.StringVar(value="Chưa chọn thư mục JSON OCR Ảnh.")
        self.selected_ocr_dir_label = ttk.Label(controls_frame, textvariable=self.selected_ocr_dir_label_var, wraplength=300)
        self.selected_ocr_dir_label.pack(side=tk.LEFT, padx=(0,10), fill=tk.X, expand=True)

        self.refresh_button = ttk.Button(controls_frame, text="Tải/Làm mới dữ liệu bảng", command=self._load_data_into_table)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))

        self.debug_button = ttk.Button(controls_frame, text="Kiểm tra JSON Phạm Nhân", command=self._debug_json_files)
        self.debug_button.pack(side=tk.LEFT)

        table_frame = ttk.Frame(parent_frame_for_visualize)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        cols = ('stt', 'hoVaTen', 'namSinh', 'noiDangKyHKTT', 'toiDanh', 'maPhamNhan', 'loaiTNThuocHe', 'hoTenBo', 'hoTenMe', 'soNgayRaQD', 'donViRaQD', 'sourceFile') # Keep sourceFile
        col_names = ('STT', 'Họ và Tên', 'Năm Sinh', 'Nơi ĐK HKTT', 'Tội Danh', 'Mã Phạm Nhân', 'Loại TN', 'Họ Tên Bố', 'Họ Tên Mẹ', 'Số Ngày Ra QĐ', 'ĐV Ra QĐ', 'File Nguồn') # Keep File Nguồn
        
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col_idx, (col_id, name) in enumerate(zip(cols, col_names)):
            self.tree.heading(col_id, text=name)
            width = 100
            if col_id == 'hoVaTen': width = 150
            elif col_id == 'noiDangKyHKTT': width = 200
            elif col_id == 'toiDanh': width = 150
            elif col_id == 'stt': width = 40
            elif col_id == 'sourceFile': width = 150
            self.tree.column(col_id, width=width, anchor=tk.W, stretch=tk.YES if col_id in ['hoVaTen', 'noiDangKyHKTT', 'toiDanh'] else tk.NO)

        # Add double-click event binding
        self.tree.bind('<Double-1>', self._on_double_click)

        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _on_double_click(self, event):
        """Handle double-click event on tree item"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        
        # Get the values of the selected row
        values = self.tree.item(item, 'values')
        if not values:
            return
        
        # Extract person name and source file
        person_name = values[1]  # hoVaTen column
        source_file = values[11]  # sourceFile column
        
        if not person_name or not source_file:
            messagebox.showwarning("Thông báo", "Không thể xác định thông tin người hoặc file nguồn.", parent=self.parent_tab)
            return
        
        # Open the document statistics window with source filename
        try:
            DocumentStatsWindow(self.parent_tab, person_name, source_file)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi mở cửa sổ thống kê: {str(e)}", parent=self.parent_tab)

    def _select_ocr_json_directory(self):
        directory = filedialog.askdirectory(title="Chọn thư mục chứa file JSON từ OCR Ảnh", parent=self.parent_tab)
        if directory and os.path.isdir(directory):
            self.ocr_json_dir = directory
            self.selected_ocr_dir_label_var.set(f"Thư mục OCR Ảnh: ...{os.sep}{os.path.basename(directory)}")
            self._load_data_into_table() # Automatically load data after selecting a new directory
        else:
            # User cancelled or closed dialog, keep existing or no directory
            if not self.ocr_json_dir:
                self.selected_ocr_dir_label_var.set("Chưa chọn thư mục OCR Ảnh.")

    def _debug_json_files(self):
        """Debug function to check JSON files structure"""
        if not self.ocr_json_dir:
            messagebox.showwarning("Thiếu thư mục", "Vui lòng chọn thư mục chứa file JSON trước.", parent=self.parent_tab)
            return
            
        if not os.path.isdir(self.ocr_json_dir):
            messagebox.showwarning("Lỗi thư mục", f"Thư mục '{self.ocr_json_dir}' không tồn tại.", parent=self.parent_tab)
            return

        debug_info = []
        json_files_found = 0
        
        # Get all JSON files and sort them
        all_files = [f for f in os.listdir(self.ocr_json_dir) if f.endswith(".json")]
        all_files.sort()
        
        for filename in all_files:
            json_files_found += 1
            filepath = os.path.join(self.ocr_json_dir, filename)
            debug_info.append(f"\n--- File: {filename} ---")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                debug_info.append(f"✓ JSON hợp lệ")
                debug_info.append(f"Các key chính: {list(data.keys())}")
                
                if "danhSachPhamNhan" in data:
                    danh_sach_pham_nhan = data["danhSachPhamNhan"]
                    if isinstance(danh_sach_pham_nhan, list):
                        debug_info.append(f"✓ Có 'danhSachPhamNhan' với {len(danh_sach_pham_nhan)} mục")
                        if len(danh_sach_pham_nhan) > 0:
                            first_item = danh_sach_pham_nhan[0]
                            if isinstance(first_item, dict):
                                debug_info.append(f"Mục đầu tiên có các trường: {list(first_item.keys())}")
                            else:
                                debug_info.append(f"⚠ Mục đầu tiên không phải dict: {type(first_item)}")
                    else:
                        debug_info.append(f"⚠ 'danhSachPhamNhan' không phải list: {type(danh_sach_pham_nhan)}")
                else:
                    debug_info.append("✗ Không có key 'danhSachPhamNhan'")
                
                # Check for danhSachTaiLieu as well
                if "danhSachTaiLieu" in data:
                    danh_sach_tai_lieu = data["danhSachTaiLieu"]
                    if isinstance(danh_sach_tai_lieu, list):
                        debug_info.append(f"✓ Có 'danhSachTaiLieu' với {len(danh_sach_tai_lieu)} mục")
                    else:
                        debug_info.append(f"⚠ 'danhSachTaiLieu' không phải list: {type(danh_sach_tai_lieu)}")
                else:
                    debug_info.append("⚠ Không có key 'danhSachTaiLieu'")
                    
                # Show first few characters of file content
                with open(filepath, 'r', encoding='utf-8') as f:
                    content_preview = f.read(200)
                debug_info.append(f"Nội dung đầu file: {content_preview}...")
                    
            except json.JSONDecodeError as e:
                debug_info.append(f"✗ JSON không hợp lệ: {e}")
                # Try to show file content
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read(500)  # First 500 chars
                    debug_info.append(f"Nội dung file: {content}")
                except Exception as read_err:
                    debug_info.append(f"Không thể đọc file: {read_err}")
                    
            except Exception as e:
                debug_info.append(f"✗ Lỗi khác: {e}")
        
        if json_files_found == 0:
            debug_info.append("Không tìm thấy file .json nào trong thư mục.")
        
        # Show debug info in a new window
        debug_window = tk.Toplevel(self.parent_tab)
        debug_window.title("Thông tin Debug JSON")
        debug_window.geometry("800x600")
        
        debug_text = scrolledtext.ScrolledText(debug_window, wrap=tk.WORD)
        debug_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        debug_text.insert(tk.END, f"Thư mục được kiểm tra: {self.ocr_json_dir}\n")
        debug_text.insert(tk.END, f"Số file JSON tìm thấy: {json_files_found}\n")
        debug_text.insert(tk.END, "\n".join(debug_info))
        
        debug_text.config(state=tk.DISABLED)

    def _load_data_into_table(self):
        """Load data from all JSON files in the selected directory"""
        # Clear existing data
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        loaded_count = 0
        error_files = []
        
        # Check if directory is selected
        if not self.ocr_json_dir:
            messagebox.showwarning("Thiếu thư mục", "Vui lòng chọn thư mục chứa file JSON từ OCR Ảnh trước.", parent=self.parent_tab)
            return
            
        try:
            if not os.path.isdir(self.ocr_json_dir):
                messagebox.showwarning("Thiếu thư mục", f"Thư mục '{self.ocr_json_dir}' không tồn tại. Không thể tải dữ liệu.", parent=self.parent_tab)
                return

            # Get all JSON files and sort them
            json_files = [f for f in os.listdir(self.ocr_json_dir) if f.endswith(".json")]
            json_files.sort()  # This ensures file1.json, file2.json, file3.json, file4.json order
            
            if not json_files:
                messagebox.showinfo("Thông tin", f"Không tìm thấy file JSON nào trong thư mục:\n'{self.ocr_json_dir}'", parent=self.parent_tab)
                return

            # Load data from all files sequentially
            for filename in json_files:
                filepath = os.path.join(self.ocr_json_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Check if data has the expected structure
                    if not isinstance(data, dict):
                        error_files.append(f"{filename}: Root không phải dict")
                        continue
                        
                    danh_sach_pham_nhan = data.get("danhSachPhamNhan", [])
                    if not isinstance(danh_sach_pham_nhan, list):
                        error_files.append(f"{filename}: 'danhSachPhamNhan' không phải list")
                        continue
                        
                    if len(danh_sach_pham_nhan) == 0:
                        error_files.append(f"{filename}: 'danhSachPhamNhan' rỗng")
                        continue
                        
                    # Add all records from this file
                    for item_idx, item in enumerate(danh_sach_pham_nhan):
                        if isinstance(item, dict):
                            values = (
                                item.get("stt", ""), item.get("hoVaTen", ""), item.get("namSinh", ""),
                                item.get("noiDangKyHKTT", ""), item.get("toiDanh", ""), item.get("maPhamNhan", ""),
                                item.get("loaiTNThuocHe", ""), item.get("hoTenBo", ""), item.get("hoTenMe", ""),
                                item.get("soNgayRaQD", ""), item.get("donViRaQD", ""),
                                filename # Add source filename to the tuple
                            )
                            source_base_name = os.path.splitext(filename)[0]
                            row_iid = f"{source_base_name}_{item_idx}" # Unique ID for the row
                            self.tree.insert("", tk.END, values=values, iid=row_iid, tags=(source_base_name,))
                            loaded_count += 1
                        else:
                            error_files.append(f"{filename}: Mục {item_idx} không phải dict")
                            
                except json.JSONDecodeError as e:
                    error_files.append(f"{filename}: JSON không hợp lệ - {str(e)}")
                except UnicodeDecodeError as e:
                    error_files.append(f"{filename}: Lỗi encoding - {str(e)}")
                except Exception as e:
                    error_files.append(f"{filename}: Lỗi khác - {str(e)}")
            
            # Show results
            message_parts = []
            if loaded_count > 0:
                message_parts.append(f"Đã tải thành công {loaded_count} bản ghi từ {len(json_files)} file JSON (nối tiếp).")
                message_parts.append("Tip: Double-click vào tên người để xem thống kê tài liệu.")
            
            if error_files:
                message_parts.append(f"\nCó lỗi với {len(error_files)} file:")
                message_parts.extend([f"- {error}" for error in error_files[:10]])  # Show first 10 errors
                if len(error_files) > 10:
                    message_parts.append(f"... và {len(error_files) - 10} lỗi khác.")
                message_parts.append("\nHãy sử dụng nút 'Kiểm tra JSON' để xem chi tiết.")
            
            if loaded_count == 0:
                messagebox.showwarning("Không có dữ liệu", "\n".join(message_parts), parent=self.parent_tab)
            elif error_files:
                messagebox.showinfo("Tải dữ liệu hoàn tất với lỗi", "\n".join(message_parts), parent=self.parent_tab)
            else:
                messagebox.showinfo("Thành công", "\n".join(message_parts), parent=self.parent_tab)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu từ '{self.ocr_json_dir}': {e}", parent=self.parent_tab)

def create_ui(app_instance, parent_tab):
    """Tạo giao diện cho Tab Visualize."""
    VisualizeTab(app_instance, parent_tab)
    ########PDF