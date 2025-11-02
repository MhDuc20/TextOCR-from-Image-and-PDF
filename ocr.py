import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import requests
import json
import datetime

def call_ocr_api_from_python(image_path, api_url="http://192.168.0.118:5000/describe_image", model=None, prompt=None):
    print(f"--- Gọi API OCR ---")
    print(f"Đường dẫn ảnh: {image_path}")
    print(f"URL API: {api_url}")
    try:
        with open(image_path, 'rb') as image_file:
            filename_in_request = os.path.basename(image_path)
            files = {'image': (filename_in_request, image_file, 'image/jpeg')}
            data = {}
            if model:
                data['model'] = model
            if prompt:
                data['prompt'] = prompt
            print(f"Tham số 'files': {files['image'][0]} (loại: {files['image'][2]})")
            print(f"Tham số 'data': {data}")
            response = requests.post(api_url, files=files, data=data, timeout=300)
            response.raise_for_status()
            return response.json()
    except FileNotFoundError:
        return {"error": f"Không tìm thấy file ảnh tại '{image_path}'"}
    except requests.exceptions.Timeout:
        return {"error": f"Hết thời gian chờ khi gọi API."}
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try: error_detail = e.response.json()
            except ValueError: error_detail = e.response.text
        return {"error": f"Lỗi API: {error_detail}"}
    except Exception as e:
        return {"error": f"Lỗi không mong muốn: {e}"}

class SearchWindow(tk.Toplevel):
    def __init__(self, parent, json_data_dir):
        super().__init__(parent)
        self.title("Tìm Kiếm Dữ Liệu OCR")
        self.geometry("1400x600")
        self.json_data_dir = json_data_dir
        self.parent_app = parent

        search_frame = ttk.Frame(self, padding="10")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Nhập từ khóa tìm kiếm:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_term_entry = ttk.Entry(search_frame, width=50)
        self.search_term_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.search_button = ttk.Button(search_frame, text="Tìm Kiếm", command=self.perform_search)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.clear_button = ttk.Button(search_frame, text="Xóa Kết Quả", command=self.clear_results)
        self.clear_button.grid(row=0, column=3, padx=5, pady=5)

        search_frame.columnconfigure(1, weight=1)

        results_frame = ttk.Frame(self, padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_tree = ttk.Treeview(results_frame,
                                         columns=("filename", "source_field", "stt", "hoVaTen", "namSinh", "noiDangKyHKTT", "toiDanh", "maPhamNhan", "loaiTNThuocHe", "hoTenBo", "hoTenMe", "soNgayRaQD", "donViRaQD"),
                                         show="headings")
        self.results_tree.heading("filename", text="Tên File")
        self.results_tree.heading("source_field", text="Nguồn/Trường") 
        self.results_tree.heading("stt", text="STT")
        self.results_tree.heading("hoVaTen", text="Họ và Tên")
        self.results_tree.heading("namSinh", text="Năm Sinh")
        self.results_tree.heading("noiDangKyHKTT", text="Nơi ĐK HKTT")
        self.results_tree.heading("toiDanh", text="Tội Danh")
        self.results_tree.heading("maPhamNhan", text="Mã Phạm Nhân")
        self.results_tree.heading("loaiTNThuocHe", text="Loại TN Thuộc Hệ")
        self.results_tree.heading("hoTenBo", text="Họ Tên Bố")
        self.results_tree.heading("hoTenMe", text="Họ Tên Mẹ")
        self.results_tree.heading("soNgayRaQD", text="Số, Ngày Ra QĐ")
        self.results_tree.heading("donViRaQD", text="Đơn Vị Ra QĐ")

        self.results_tree.column("filename", width=120, stretch=tk.NO, anchor="w")
        self.results_tree.column("source_field", width=150, anchor="w")
        self.results_tree.column("stt", width=50, anchor="center")
        self.results_tree.column("hoVaTen", width=150, anchor="w")
        self.results_tree.column("namSinh", width=80, anchor="center")
        self.results_tree.column("noiDangKyHKTT", width=180, anchor="w")
        self.results_tree.column("toiDanh", width=120, anchor="w")
        self.results_tree.column("maPhamNhan", width=120, anchor="center")
        self.results_tree.column("loaiTNThuocHe", width=120, anchor="w")
        self.results_tree.column("hoTenBo", width=120, anchor="w")
        self.results_tree.column("hoTenMe", width=120, anchor="w")
        self.results_tree.column("soNgayRaQD", width=120, anchor="center")
        self.results_tree.column("donViRaQD", width=180, anchor="w")

        self.results_tree.tag_configure('thongTinChungMatch', background='#D8E6FF')
        self.results_tree.tag_configure('taiLieuItem', background='#FFFFFF')
        self.results_tree.tag_configure('taiLieuMatchDirect', background='#E0FFE0')

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        self.status_bar = ttk.Label(self, text="Sẵn sàng tìm kiếm.", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def clear_results(self):
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)
        self.status_bar.config(text="Đã xóa kết quả. Sẵn sàng tìm kiếm.")

    def _add_thong_tin_chung_match_to_tree(self, filename, field_name, field_value):
        self.results_tree.insert("", tk.END, values=(
            os.path.basename(filename),
            f"TT Chung: {field_name}",
            str(field_value)[:200],
            "", "", "", "", "", "", "", "", "", ""
        ), tags=('thongTinChungMatch',))

    def _add_pham_nhan_item_to_tree(self, filename, item, is_direct_match=False, matched_key_in_dsl=None):
        tag_to_use = 'taiLieuMatchDirect' if is_direct_match else 'taiLieuItem'
        
        source_field_display = ""
        if is_direct_match and matched_key_in_dsl:
            source_field_display = f"DS Phạm Nhân: {matched_key_in_dsl}"

        self.results_tree.insert("", tk.END, values=(
            os.path.basename(filename) if is_direct_match else "",
            source_field_display,
            item.get("stt", ""),
            item.get("hoVaTen", ""),
            item.get("namSinh", ""),
            item.get("noiDangKyHKTT", ""),
            item.get("toiDanh", ""),
            item.get("maPhamNhan", ""),
            item.get("loaiTNThuocHe", ""),
            item.get("hoTenBo", ""),
            item.get("hoTenMe", ""),
            item.get("soNgayRaQD", ""),
            item.get("donViRaQD", "")
        ), tags=(tag_to_use,))

    def perform_search(self):
        search_term = self.search_term_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập từ khóa tìm kiếm.", parent=self)
            return

        self.clear_results()
        self.status_bar.config(text=f"Đang tìm kiếm '{search_term}'...")
        self.update_idletasks()

        found_files_count = 0
        processed_files_for_tt_chung_match = set()

        try:
            for filename_short in os.listdir(self.json_data_dir):
                if filename_short.endswith(".json"):
                    filepath = os.path.join(self.json_data_dir, filename_short)
                    current_file_has_any_match = False
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        match_in_thong_tin_chung = False
                        tt_chung = data.get("thongTinChung")
                        if isinstance(tt_chung, dict):
                            for key_ttc, value_ttc in tt_chung.items():
                                if value_ttc is not None and search_term.lower() in str(value_ttc).lower():
                                    if not current_file_has_any_match:
                                        found_files_count += 1
                                        current_file_has_any_match = True
                                    
                                    self._add_thong_tin_chung_match_to_tree(filepath, key_ttc, value_ttc)
                                    match_in_thong_tin_chung = True
                                    processed_files_for_tt_chung_match.add(filepath)
                                    
                                    ds_pham_nhan_ttc = data.get("danhSachPhamNhan")
                                    if isinstance(ds_pham_nhan_ttc, list):
                                        for item_dsl_ttc in ds_pham_nhan_ttc:
                                            if isinstance(item_dsl_ttc, dict):
                                                self._add_pham_nhan_item_to_tree(filepath, item_dsl_ttc)
                                    break

                        if filepath not in processed_files_for_tt_chung_match:
                            ds_pham_nhan = data.get("danhSachPhamNhan")
                            if isinstance(ds_pham_nhan, list):
                                for item_dsl in ds_pham_nhan:
                                    if isinstance(item_dsl, dict):
                                        for key_dsl, value_dsl in item_dsl.items():
                                            if value_dsl is not None and search_term.lower() in str(value_dsl).lower():
                                                if not current_file_has_any_match:
                                                    found_files_count += 1
                                                    current_file_has_any_match = True
                                                self._add_pham_nhan_item_to_tree(filepath, item_dsl, 
                                                                              is_direct_match=True, 
                                                                              matched_key_in_dsl=key_dsl)

                    except json.JSONDecodeError:
                        print(f"Lỗi: File {filename_short} không phải JSON hợp lệ.")
                    except Exception as e:
                        print(f"Lỗi khi xử lý file {filename_short}: {e}")
            
            total_results_lines = len(self.results_tree.get_children())
            if found_files_count > 0:
                self.status_bar.config(text=f"Tìm thấy khớp trong {found_files_count} file ({total_results_lines} dòng hiển thị) cho '{search_term}'.")
            else:
                self.status_bar.config(text=f"Không tìm thấy kết quả nào cho '{search_term}'.")

        except Exception as e:
            messagebox.showerror("Lỗi tìm kiếm", f"Đã xảy ra lỗi trong quá trình tìm kiếm: {e}", parent=self)
            self.status_bar.config(text="Lỗi trong quá trình tìm kiếm.")

class OCRAppSimple:
    # Updated prompt for extracting 'danhSachTaiLieu' with complete structure
    PROMPT_FOR_JSON_EXTRACTION = (
        "Trích xuất thông tin từ hình ảnh và trả về dưới dạng một đối tượng JSON duy nhất.\n"
        "Đối tượng JSON PHẢI chứa cấu trúc sau:\n"
        "1. 'danhSachTaiLieu': một mảng các đối tượng tài liệu, mỗi đối tượng PHẢI chứa các trường: 'stt' (số thứ tự, kiểu số), 'trichYeu' (trích yếu, kiểu chuỗi), 'soTo' (số tờ, kiểu chuỗi), 'dacDiem' (đặc điểm, kiểu chuỗi), 'doMat' (độ mật, kiểu chuỗi hoặc null), 'ghiChu' (ghi chú, kiểu chuỗi hoặc null).\n"
        "2. 'thongTinChung': một đối tượng chứa thông tin chung với các trường: 'mauSo' (mẫu số), 'vanBanHuongDan' (văn bản hướng dẫn), 'ngayBanHanhVanBan' (ngày ban hành văn bản), 'tieuDe' (tiêu đề), 'soHoSo' (số hồ sơ).\n"
        "Nếu một trường không có giá trị hoặc không xác định được từ ảnh, hãy để giá trị là null (cho số hoặc đối tượng) hoặc chuỗi rỗng \"\" (cho chuỗi văn bản).\n"
        "Quan trọng: Toàn bộ phản hồi PHẢI LÀ một đối tượng JSON hợp lệ duy nhất, không có bất kỳ văn bản giải thích, markdown formatting (như ```json ... ```) hoặc tiền tố/hậu tố nào khác xung quanh nó.\n"
        "Ví dụ cấu trúc JSON mong muốn:\n"
        "{\n"
        "  \"danhSachTaiLieu\": [\n"
        "    {\n"
        "      \"stt\": 1,\n"
        "      \"trichYeu\": \"Quyết định lập hồ sơ\",\n"
        "      \"soTo\": \"1-1a\",\n"
        "      \"dacDiem\": \"Bản gốc\",\n"
        "      \"doMat\": null,\n"
        "      \"ghiChu\": null\n"
        "    }\n"
        "  ],\n"
        "  \"thongTinChung\": {\n"
        "    \"mauSo\": \"B3\",\n"
        "    \"vanBanHuongDan\": \"BH theo TT số 26/2023/TT-BCA\",\n"
        "    \"ngayBanHanhVanBan\": \"03/07/2023\",\n"
        "    \"tieuDe\": \"THỐNG KÊ TÀI LIỆU CÓ TRONG HỒ SƠ\",\n"
        "    \"soHoSo\": \"00222419884\"\n"
        "  }\n"
        "}"
    )

    def __init__(self, master):
        self.master = master
        master.title("OCR Client (Lưu và Tìm Kiếm JSON)")
        master.geometry("600x400") 

        self.selected_image_path_var = tk.StringVar()
        self.full_selected_image_path = ""
        self.api_url_default = "http://192.168.0.118:5000/describe_image" 
        self.json_output_dir = "json_results"

        os.makedirs(self.json_output_dir, exist_ok=True)

        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        api_url_frame = ttk.LabelFrame(main_frame, text="API Endpoint")
        api_url_frame.pack(fill=tk.X, pady=5)
        ttk.Label(api_url_frame, text="URL:").pack(side=tk.LEFT, padx=5, pady=5)
        self.api_url_entry = ttk.Entry(api_url_frame, width=50)
        self.api_url_entry.insert(0, self.api_url_default)
        self.api_url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        model_frame = ttk.LabelFrame(main_frame, text="Model OCR")
        model_frame.pack(fill=tk.X, pady=5)
        ttk.Label(model_frame, text="Model (tùy chọn):").pack(side=tk.LEFT, padx=5, pady=5)
        self.model_entry = ttk.Entry(model_frame, width=40)
        self.model_entry.insert(0, "qwen2.5vl:7b")  

        self.model_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        image_frame = ttk.LabelFrame(main_frame, text="Chọn Ảnh")
        image_frame.pack(fill=tk.X, pady=5)
        self.select_image_button = ttk.Button(image_frame, text="Duyệt Ảnh...", command=self.browse_image)
        self.select_image_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.image_path_label = ttk.Label(image_frame, textvariable=self.selected_image_path_var, wraplength=350)
        self.selected_image_path_var.set("Chưa chọn ảnh nào.")
        self.image_path_label.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self.submit_button = ttk.Button(main_frame, text="Gọi OCR API và Lưu JSON", command=self.submit_ocr_request)
        self.submit_button.pack(pady=10, fill=tk.X)

        self.open_search_button = ttk.Button(main_frame, text="Mở Cửa Sổ Tìm Kiếm", command=self.open_search_window)
        self.open_search_button.pack(pady=5, fill=tk.X)
        
        self.status_label = ttk.Label(main_frame, text="Trạng thái: Sẵn sàng", wraplength=580, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(pady=10, fill=tk.X, side=tk.BOTTOM)

    def open_search_window(self):
        if not hasattr(self, "search_win_instance") or not self.search_win_instance.winfo_exists():
            self.search_win_instance = SearchWindow(self.master, self.json_output_dir)
            self.search_win_instance.grab_set() 
        else:
            self.search_win_instance.lift() 
            self.search_win_instance.focus_set()

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file ảnh",
            filetypes=(("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png"), ("All files", "*.*"))
        )
        if file_path:
            self.full_selected_image_path = file_path
            parent_folder = os.path.basename(os.path.dirname(file_path))
            file_name = os.path.basename(file_path)
            display_path = os.path.join("...", parent_folder, file_name) if parent_folder else file_name
            self.selected_image_path_var.set(display_path)
            self.set_status(f"Đã chọn: {display_path}")
        else:
            self.selected_image_path_var.set("Chưa chọn ảnh nào.")
            self.full_selected_image_path = ""
            self.set_status("Trạng thái: Sẵn sàng")

    def set_status(self, message, is_error=False):
        self.status_label.config(text=message, foreground="red" if is_error else "black")
        self.master.update_idletasks()

    def submit_ocr_request(self):
        actual_file_path = self.full_selected_image_path
        api_url = self.api_url_entry.get().strip()
        model = self.model_entry.get().strip()

        if not actual_file_path:
            self.set_status("Lỗi: Vui lòng chọn một file ảnh.", is_error=True)
            messagebox.showerror("Lỗi", "Vui lòng chọn một file ảnh.")
            return
        if not api_url:
            self.set_status("Lỗi: Vui lòng nhập URL của API.", is_error=True)
            messagebox.showerror("Lỗi", "Vui lòng nhập URL của API.")
            return

        json_prompt = self.PROMPT_FOR_JSON_EXTRACTION

        self.set_status(f"Đang xử lý ảnh: {os.path.basename(actual_file_path)}... Vui lòng đợi.")
        model_to_send = model if model else None
        response_data = call_ocr_api_from_python(
            image_path=actual_file_path, api_url=api_url, model=model_to_send, prompt=json_prompt
        )

        if response_data is None:
            self.set_status("Lỗi: Không nhận được phản hồi từ API.", is_error=True)
            messagebox.showerror("Lỗi API", "Không nhận được phản hồi từ API hoặc có lỗi không xác định.")
            return
        if "error" in response_data:
            error_msg = response_data['error']
            self.set_status(f"Lỗi từ API OCR: {error_msg}", is_error=True)
            messagebox.showerror("Lỗi API OCR", f"Lỗi: {error_msg}")
            return

        OCRAppSimple._save_json_data_to_file(self, response_data, actual_file_path, self.json_output_dir, self.set_status, self.master)

    @staticmethod
    def _normalize_json_structure(data_dict):
        """
        Đảm bảo dữ liệu JSON có khóa 'danhSachTaiLieu' (list) và 'thongTinChung' (dict).
        """
        if not isinstance(data_dict, dict):
            # Nếu AI trả về một danh sách tài liệu trực tiếp, giả sử đó là danhSachTaiLieu.
            if isinstance(data_dict, list):
                print(f"ℹ️ _normalize_json_structure: Input data is a list. Wrapping it under 'danhSachTaiLieu'.")
                return {"danhSachTaiLieu": data_dict, "thongTinChung": {}}
            # Nếu không phải dict hoặc list, đó là định dạng không mong muốn.
            print(f"⚠️ _normalize_json_structure: Input data is not a dict or list, but {type(data_dict)}. Returning empty structure.")
            return {"danhSachTaiLieu": [], "thongTinChung": {}}

        normalized_data = {}

        # Xử lý 'danhSachTaiLieu'
        danh_sach_tai_lieu = data_dict.get("danhSachTaiLieu")
        if isinstance(danh_sach_tai_lieu, list):
            normalized_data["danhSachTaiLieu"] = danh_sach_tai_lieu
        elif isinstance(danh_sach_tai_lieu, dict): # Nếu AI trả về một mục đơn lẻ không nằm trong danh sách
            normalized_data["danhSachTaiLieu"] = [danh_sach_tai_lieu]
        else: # Thiếu hoặc sai kiểu dữ liệu
            normalized_data["danhSachTaiLieu"] = []

        # Xử lý 'thongTinChung'
        thong_tin_chung = data_dict.get("thongTinChung")
        if isinstance(thong_tin_chung, dict):
            normalized_data["thongTinChung"] = thong_tin_chung
        else: # Thiếu hoặc sai kiểu dữ liệu
            normalized_data["thongTinChung"] = {}
            
        # Bảo toàn các khóa khác nếu có (mặc dù prompt khá cụ thể)
        for key, value in data_dict.items():
            if key not in normalized_data: # Chỉ thêm nếu chưa được xử lý (danhSachTaiLieu, thongTinChung)
                normalized_data[key] = value
        return normalized_data

    @staticmethod
    def _save_json_data_to_file(instance_or_none, response_data, original_image_path, default_json_output_dir, status_callback, parent_widget_for_messagebox):
        """
        Xử lý phản hồi từ API, cố gắng parse nó thành JSON, chuẩn hóa cấu trúc, lưu vào file, và trả về dữ liệu JSON đã parse.
        """
        ocr_text_content = ""
        parsed_json_data_directly = None
        final_data_to_save_and_return = None

        # Extract text/JSON from API response
        if isinstance(response_data, dict) and "text" in response_data:
            ocr_text_content = response_data['text']
        elif isinstance(response_data, str):
             ocr_text_content = response_data
        elif isinstance(response_data, dict): 
            parsed_json_data_directly = response_data
        else:
            status_callback(f"Lỗi: API trả về định dạng không rõ ràng: {type(response_data)}", is_error=True)
            messagebox.showerror("Lỗi Định Dạng", f"API trả về định dạng không rõ ràng.\nDữ liệu: {str(response_data)[:500]}...", parent=parent_widget_for_messagebox)
            return None

        # Parse JSON data
        if parsed_json_data_directly:
            final_data_to_save_and_return = parsed_json_data_directly
            # Handle JSON inside "description" field
            if "description" in final_data_to_save_and_return:
                desc_content = final_data_to_save_and_return["description"]
                if isinstance(desc_content, str) and desc_content.strip().startswith("```json"):
                    try:
                        cleaned_desc = desc_content.strip()
                        if cleaned_desc.startswith("```json"):
                            cleaned_desc = cleaned_desc[7:]
                        if cleaned_desc.endswith("```"):
                            cleaned_desc = cleaned_desc[:-3]
                        final_data_to_save_and_return = json.loads(cleaned_desc.strip(), strict=False)
                    except json.JSONDecodeError:
                        pass 
            
        elif ocr_text_content: 
            try:
                cleaned_json_string = ocr_text_content.strip()
                if cleaned_json_string.startswith("```json"): 
                    cleaned_json_string = cleaned_json_string[7:]
                if cleaned_json_string.endswith("```"): 
                    cleaned_json_string = cleaned_json_string[:-3]
                final_data_to_save_and_return = json.loads(cleaned_json_string.strip(), strict=False)
            except json.JSONDecodeError as e:
                status_callback(f"Lỗi: API trả về văn bản không phải JSON hợp lệ. Chi tiết: {e}", is_error=True)
                messagebox.showerror("Lỗi JSON", f"API trả về văn bản không phải là JSON hợp lệ.\nChi tiết: {e}\nDữ liệu:\n{ocr_text_content[:500]}...", parent=parent_widget_for_messagebox)
                return None
            except Exception as ex:
                status_callback(f"Lỗi không xác định khi xử lý phản hồi: {ex}", is_error=True)
                messagebox.showerror("Lỗi Xử Lý", f"Lỗi không xác định khi xử lý phản hồi JSON.\nChi tiết: {ex}", parent=parent_widget_for_messagebox)
                return None
        
        if final_data_to_save_and_return is None:
            status_callback("Lỗi: API không trả về nội dung văn bản hoặc đối tượng JSON hợp lệ.", is_error=True)
            messagebox.showerror("Lỗi API", "API không trả về nội dung văn bản hoặc đối tượng JSON hợp lệ.", parent=parent_widget_for_messagebox)
            return None

        # Normalize JSON structure to match the expected format
        final_data_to_save_and_return = OCRAppSimple._normalize_json_structure(final_data_to_save_and_return)

        # Determine output directory
        actual_output_dir = default_json_output_dir
        if isinstance(final_data_to_save_and_return, dict) and \
        "danhSachTaiLieu" in final_data_to_save_and_return:
            actual_output_dir = "thong_ke"
            if isinstance(final_data_to_save_and_return.get("danhSachTaiLieu"), list):
                if len(final_data_to_save_and_return.get("danhSachTaiLieu")) > 0:
                    print(f"ℹ️ Phát hiện 'danhSachTaiLieu' (có nội dung). Lưu vào thư mục '{actual_output_dir}'.")
                else:
                    print(f"ℹ️ Phát hiện 'danhSachTaiLieu' (rỗng). Lưu vào thư mục '{actual_output_dir}' cho loại tài liệu này.")
            else:
                print(f"ℹ️ Phát hiện key 'danhSachTaiLieu' nhưng không phải list. Lưu vào thư mục '{actual_output_dir}'.")
        else:
            # If no 'danhSachTaiLieu' key
            print(f"ℹ️ Không phát hiện key 'danhSachTaiLieu'. Lưu vào thư mục mặc định: {actual_output_dir}")

        os.makedirs(actual_output_dir, exist_ok=True)
        base_name_without_ext, _ = os.path.splitext(os.path.basename(original_image_path))
        json_filename = f"{base_name_without_ext}.json"
        full_json_path = os.path.join(actual_output_dir, json_filename)
        try:
            with open(full_json_path, 'w', encoding='utf-8') as f:
                json.dump(final_data_to_save_and_return, f, ensure_ascii=False, indent=4)
            success_msg = f"Thành công! Kết quả đã lưu vào: {full_json_path}"
            status_callback(success_msg) 
            return final_data_to_save_and_return 
        except TypeError as te:
            error_msg = f"Lỗi khi lưu JSON: Dữ liệu không thể tuần tự hóa. Chi tiết: {te}"
            status_callback(error_msg, is_error=True); print(error_msg)
            messagebox.showerror("Lỗi Lưu File OCR", f"{error_msg}\nDữ liệu:\n{str(final_data_to_save_and_return)[:500]}", parent=parent_widget_for_messagebox)
            return None 
        except Exception as e:
            error_msg = f"Lỗi khi lưu kết quả vào file JSON '{full_json_path}': {e}"
            status_callback(error_msg, is_error=True); print(error_msg)
            messagebox.showerror("Lỗi Lưu File OCR", error_msg, parent=parent_widget_for_messagebox)
            return None 
        
    @staticmethod
    def _actual_save_to_json_file(data_to_save, original_image_path, json_output_dir, status_callback, parent_widget_for_messagebox):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    app = OCRAppSimple(root)
    root.mainloop()