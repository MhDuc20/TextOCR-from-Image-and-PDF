# app_gui.py
import tkinter as tk
from tkinter import ttk # PanedWindow, scrolledtext are imported by UI files if needed

# Import UI creation functions
from ui_tab_available_questions import create_ui as create_available_questions_ui
from ui_tab_enter_question import create_ui as create_enter_question_ui
from ui_tab_ai_response import create_ui as create_ai_response_ui # Using this as per prompt
# from ui_tab_ocr import create_ui as create_ocr_ui # Không cần tạo tab OCR riêng nữa
# from ui_tab_pdf_viewer import create_ui as create_pdf_viewer_ui # Không cần tạo tab PDF Viewer riêng nữa
from ui_tab_visualize import create_ui as create_visualize_ui # Import UI cho Tab Visualize


# Import new modules
from data_manager import DataManager
from ai_service import AIService
from handlers.available_questions_handler import AvailableQuestionsHandler
from handlers.local_search_handler import LocalSearchHandler
from handlers.ai_chat_handler import AIChatHandler # Using this as per prompt
# Import các thành phần từ ocr.py để tích hợp (bao gồm OCRAppSimple để truy cập _save_json_data_to_file)
from ocr import OCRAppSimple, SearchWindow as OCRSearchWindow, call_ocr_api_from_python
import os # Cần cho os.path.basename và os.makedirs
import json # Cần để lưu kết quả OCR PDF
import datetime # Cần cho timestamp khi lưu kết quả
from tkinter import messagebox, filedialog, scrolledtext # Thêm scrolledtext nếu chưa có
import asyncio # Thêm asyncio
import fitz  # PyMuPDF
from PIL import Image, ImageTk # Pillow
from pdf import configure_tesseract as pdf_configure_tesseract, extract_text_from_image_page

class SimpleQuestionViewerApp:
    def __init__(self, master):
        self.master = master
        master.title("Trình trả lời câu hỏi liên quan (Sử dụng AI Cục bộ)") # Updated title
        
        try:
            master.state('zoomed')
        except tk.TclError:
            screen_width = master.winfo_screenwidth()
            screen_height = master.winfo_screenheight()
            master.geometry(f"{screen_width}x{screen_height}+0+0")
            print("Lưu ý: Không thể sử dụng 'zoomed'. Đã thử đặt kích thước theo màn hình.")

        # --- Configuration ---
        # OCR specific configurations (sẽ được sử dụng bởi các phương thức OCR)
        self.ocr_selected_image_path_var = tk.StringVar()
        self.ocr_selected_image_path_var.set("Chưa chọn ảnh nào.")
        self.ocr_full_selected_image_path = ""
        self.ocr_api_url_default = "http://192.168.0.118:5000/describe_image" # Default API URL for OCR
        self.ocr_json_output_dir = "json_results"
        self.pdf_ocr_json_output_dir = "pdf_ocr_json_results" # Directory for PDF OCR JSONs
        self.pdf_split_output_dir = "pdf_split_json_results" # Directory for split PDF OCR JSONs
        self.ocr_default_model = "qwen2.5vl:7b"

        # PDF Viewer specific attributes
        self.pdf_viewer_document = None
        self.pdf_viewer_current_file_path = None # Lưu đường dẫn file PDF đang mở
        # Cấu hình Tesseract cho tab PDF Viewer (có thể đặt trong file config sau này)
        self.pdf_viewer_tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.pdf_viewer_tessdata_prefix = r'C:\Program Files\Tesseract-OCR\tessdata'
        self.asyncio = asyncio # Gán asyncio vào instance để ui_tab_visualize có thể dùng

        # --- Initialize Services ---
        self.data_manager = DataManager(self)
        self.data_manager.load_all_data()

        self.ai_service = AIService(self) # AIService no longer configures Gemini
        # self.gemini_model attribute is no longer set or used from here
        self._configure_pdf_ocr_tesseract() # Cấu hình Tesseract cho tab PDF

        # --- Initialize Handlers ---
        self.available_questions_handler = AvailableQuestionsHandler(self)
        self.local_search_handler = LocalSearchHandler(self)
        self.ai_chat_handler = AIChatHandler(self) # This will attempt to init local QA

        # --- UI State Variables ---
        self.typing_message_indices = None 

        # --- Create UI ---
        main_notebook = ttk.Notebook(master)
        main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Available Questions
        #self.tab_available_questions = ttk.Frame(main_notebook)
        #main_notebook.add(self.tab_available_questions, text="1. Danh sách câu hỏi liên quan có sẵn")
        #create_available_questions_ui(self, self.tab_available_questions)

        # Tab 2: Enter Question (Local Search)
        #self.tab_enter_question = ttk.Frame(main_notebook)
        # Updated tab title for clarity, though not strictly requested for this tab
        #main_notebook.add(self.tab_enter_question, text="2. Nhập câu hỏi (Tìm cục bộ)") 
        #create_enter_question_ui(self, self.tab_enter_question)

        # Tab 3: AI Response
        #self.tab_ai_response = ttk.Frame(main_notebook)
        #main_notebook.add(self.tab_ai_response, text="3. Hỏi AI Cục bộ") # Updated tab title
        #create_ai_response_ui(self, self.tab_ai_response) 

        # Tab 4, 5 được tích hợp vào Tab 6 (trước đây là Tab Visualize)
        # Các UI của OCR và PDF Viewer giờ được tạo bên trong ui_tab_visualize.py
        # và các widget của chúng được gán vào self.app (tức là self của SimpleQuestionViewerApp)
        # Do đó, các handler như browse_image_ocr, submit_ocr_request_ocr, pdf_viewer_open_file, etc.
        # sẽ vẫn hoạt động với các widget được tạo bởi Tab 6.

        # Tab 6: Trực quan hóa (bao gồm chức năng OCR và PDF)
        self.tab_visualize = ttk.Frame(main_notebook)
        main_notebook.add(self.tab_visualize, text="Xử lý & Trự quan dữ liệu phạm nhân") # Tên tab có thể cần cập nhật để phản ánh đúng hơn
        create_visualize_ui(self, self.tab_visualize)
        # Cập nhật command của nút trích xuất PDF để chạy hàm async
        # Điều này được thực hiện bên trong _create_pdf_processing_sub_tab của VisualizeTab
        # nên không cần gọi lại ở đây nữa.

    def _configure_pdf_ocr_tesseract(self):
        """Cấu hình Tesseract cho tab OCR PDF."""
        tess_path_to_check = self.pdf_viewer_tesseract_path
        tessdata_prefix_to_check = self.pdf_viewer_tessdata_prefix
        
        # Kiểm tra xem đường dẫn Tesseract có tồn tại không
        if not os.path.exists(tess_path_to_check):
            print(f"⚠️ CẢNH BÁO (PDF OCR): Đường dẫn Tesseract '{tess_path_to_check}' không tồn tại.")
            tess_path_to_check = None # Không thử cấu hình nếu đường dẫn không hợp lệ
        
        # Kiểm tra xem thư mục tessdata có tồn tại không
        if tessdata_prefix_to_check and not os.path.isdir(tessdata_prefix_to_check):
            print(f"⚠️ CẢNH BÁO (PDF OCR): Đường dẫn TESSDATA_PREFIX '{tessdata_prefix_to_check}' không tồn tại hoặc không phải là thư mục.")
            tessdata_prefix_to_check = None

        pdf_configure_tesseract(tesseract_cmd=tess_path_to_check, tessdata_prefix=tessdata_prefix_to_check)
        if tess_path_to_check: print(f"ℹ️ (PDF OCR) Đã cấu hình đường dẫn Tesseract: {tess_path_to_check}")
        if tessdata_prefix_to_check: print(f"ℹ️ (PDF OCR) Đã cấu hình TESSDATA_PREFIX: {tessdata_prefix_to_check}")
        if not tess_path_to_check: print("Lưu ý (PDF OCR): Tesseract chưa được cấu hình đường dẫn. OCR có thể không hoạt động.")

    # --- Methods called by UI elements (delegated to handlers) ---

    # Tab 1 related
    def filter_available_questions(self, event=None):
        self.available_questions_handler.filter_available_questions(event)

    def on_available_question_select(self, event=None):
        self.available_questions_handler.on_available_question_select(event)

    def generate_new_questions_with_ai(self):
        # This method in the handler will now show a "disabled" message
        self.available_questions_handler.generate_new_questions_with_ai()

    # Tab 2 related
    def perform_local_search(self):
        self.local_search_handler.perform_local_search()

    # Tab 3 related
    def send_to_ai(self):
        self.ai_chat_handler.send_to_ai()

    # This method is kept for potential direct calls if ever needed, but UI calls send_to_ai
    # and initial messages are handled by AIChatHandler directly or via create_ai_response_ui
    def _add_to_chat_history(self, message, sender_type="user", is_typing_message=False):
        # This method is still present in app_gui.py as per the provided file,
        # but its primary use for initial messages is now better handled directly
        # by ui_tab_ai_response.py calling the handler, or the handler itself.
        # If ui_tab_ai_response.py calls this, it will delegate to the handler.
        self.ai_chat_handler.add_to_chat_history(message, sender_type, is_typing_message)

    # --- OCR Tab related methods (adapted from ocr.OCRAppSimple) ---
    # Các widget ocr_status_label, ocr_api_url_entry, ocr_model_entry, ocr_selected_image_path_var
    # giờ đây được tạo và quản lý bởi ui_tab_visualize.py và gán vào self (app_instance)
    # nên các phương thức này sẽ hoạt động với các widget đó.
    def _ocr_set_status(self, message, is_error=False):
        if hasattr(self, 'ocr_status_label') and self.ocr_status_label: # Kiểm tra widget tồn tại
            self.ocr_status_label.config(text=f"Trạng thái OCR: {message}", foreground="red" if is_error else "black")
            self.master.update_idletasks()
        else:
            # Nếu ocr_status_label không hiển thị, có thể dùng messagebox để thông báo trạng thái quan trọng
            if is_error:
                messagebox.showerror("Lỗi OCR", message, parent=self.master)
            else:
                # Có thể hiển thị thông báo thành công qua messagebox nếu cần, hoặc chỉ log
                print(f"Trạng thái OCR: {message}")

    def _get_document_stats_prompt(self):
        """
        Trả về prompt JSON cụ thể cho việc trích xuất bảng "THỐNG KÊ TÀI LIỆU CÓ TRONG HỒ SƠ".
        """
        return (
            "Trích xuất thông tin từ hình ảnh của bảng 'THỐNG KÊ TÀI LIỆU CÓ TRONG HỒ SƠ' và trả về dưới dạng một đối tượng JSON duy nhất.\n"
            "QUAN TRỌNG: Bảng có thể được chia thành nhiều trang/hình ảnh. Hãy xử lý TUẦN TỰ từ hình ảnh đầu tiên đến cuối cùng và trích xuất TẤT CẢ các hàng.\n"
            
            "HƯỚNG DẪN XỬ LÝ NHIỀU HÌNH ẢNH:\n"
            "1. Xem xét tất cả các hình ảnh được cung cấp theo thứ tự\n"
            "2. Hình ảnh đầu tiên sẽ có tiêu đề bảng 'THỐNG KÊ TÀI LIỆU CÓ TRONG HỒ SƠ'\n"
            "3. Các hình ảnh tiếp theo có thể chỉ chứa phần tiếp theo của bảng (không có tiêu đề)\n"
            "4. Ghép nối tất cả các hàng từ tất cả hình ảnh theo thứ tự STT tăng dần\n"
            "5. Đảm bảo STT liên tục không bị gián đoạn\n"
            
            "CẤU TRÚC BẢNG:\n"
            "Bảng có 6 cột với tiêu đề:\n"
            "- TT (Số thứ tự)\n"
            "- TRÍCH YẾU TÀI LIỆU  \n"
            "- TỪ TỜ ĐẾN TỜ (hoặc SỐ TỜ)\n"
            "- ĐẶC ĐIỂM TÀI LIỆU\n"
            "- ĐỘ MẬT\n"
            "- GHI CHÚ\n"
            
            "Đối tượng JSON PHẢI chứa khóa chính:\n"
            "'danhSachTaiLieu': Một mảng các đối tượng, mỗi đối tượng đại diện cho một hàng trong bảng và PHẢI chứa các trường:\n"
            "  - 'stt' (Số thứ tự, kiểu số hoặc chuỗi nếu có ký tự đặc biệt như 'I', 'II').\n"
            "  - 'trichYeu' (Trích yếu tài liệu, kiểu chuỗi).\n"
            "  - 'tuToSo' (Từ tờ số/Số tờ, kiểu chuỗi hoặc số, ví dụ: \"1-1a\", \"2-3\", \"4\", 24, 25, \"30-31\", \"64-65\", \"75-82\", \"92-93\", \"97-100\", \"109-110\").\n"
            "  - 'dacDiem' (Đặc điểm tài liệu, kiểu chuỗi. Các giá trị phổ biến: \"Bản gốc\", \"Bản chính\", \"Bản trích sao\").\n"
            "  - 'doMat' (Độ mật, kiểu chuỗi hoặc null nếu không có).\n"
            "  - 'ghiChu' (Ghi chú, kiểu chuỗi hoặc null nếu không có).\n"
            
            "LƯU Ý QUAN TRỌNG VỀ DỮ LIỆU:\n"
            "- Cột 'TỪ TỜ ĐẾN TỜ' có thể chứa:\n"
            "  + Một số duy nhất: 4, 5, 6, 24, 25, etc.\n"
            "  + Khoảng từ số này đến số khác: \"1-1a\", \"2-3\", \"30-31\", \"64-65\", \"75-82\", \"92-93\", \"97-100\", \"109-110\"\n"
            "- Cột 'ĐẶC ĐIỂM TÀI LIỆU' chủ yếu có các giá trị: \"Bản gốc\", \"Bản chính\", \"Bản trích sao\"\n"
            "- Các cột 'ĐỘ MẬT' và 'GHI CHÚ' thường để trống (null)\n"
            "- Số thứ tự (STT) chạy liên tục từ 1 đến hết (có thể lên đến 95 hoặc cao hơn)\n"
            
            "QUY TRÌNH XỬ LÝ:\n"
            "1. Đọc hình ảnh đầu tiên (có tiêu đề bảng) và trích xuất các hàng\n"
            "2. Tiếp tục đọc các hình ảnh tiếp theo (chỉ có nội dung bảng) theo thứ tự\n"
            "3. Kết hợp tất cả các hàng theo thứ tự STT tăng dần\n"
            "4. Kiểm tra tính liên tục của STT\n"
            "5. Đảm bảo không bỏ sót hoặc trùng lặp bất kỳ hàng nào\n"
            
            "XỬ LÝ CÁC TRƯỜNG HỢP ĐẶC BIỆT:\n"
            "- Nếu một ô trong bảng trống hoặc không đọc được, gán giá trị null\n"
            "- Nếu STT có ký tự đặc biệt (như I, II, III), giữ nguyên dưới dạng chuỗi\n"
            "- Nếu cột 'TỪ TỜ ĐẾN TỜ' có dấu gạch ngang (-), giữ nguyên format chuỗi\n"
            "- Loại bỏ khoảng trắng thừa ở đầu và cuối mỗi giá trị\n"
            
            "KIỂM TRA CHẤT LƯỢNG:\n"
            "- Đảm bảo số lượng hàng phù hợp với STT cuối cùng\n"
            "- Kiểm tra không có STT bị thiếu hoặc trùng lặp\n"
            "- Xác minh các giá trị 'dacDiem' thuộc một trong các loại đã liệt kê\n"
            
            "Quan trọng: Toàn bộ phản hồi PHẢI LÀ một đối tượng JSON hợp lệ duy nhất, không có bất kỳ văn bản giải thích, markdown formatting (như ```json ... ```) hoặc tiền tố/hậu tố nào khác xung quanh nó.\n"
            
            "Ví dụ cấu trúc JSON mong muốn:\n"
            "{\n"
            "  \"danhSachTaiLieu\": [\n"
            "    {\n"
            "      \"stt\": 1,\n"
            "      \"trichYeu\": \"Quyết định lập hồ sơ\",\n"
            "      \"tuToSo\": \"1-1a\",\n"
            "      \"dacDiem\": \"Bản gốc\",\n"
            "      \"doMat\": null,\n"
            "      \"ghiChu\": null\n"
            "    },\n"
            "    {\n"
            "      \"stt\": 23,\n"
            "      \"trichYeu\": \"Quyết định gia hạn tạm giam\",\n"
            "      \"tuToSo\": 24,\n"
            "      \"dacDiem\": \"Bản chính\",\n"
            "      \"doMat\": null,\n"
            "      \"ghiChu\": null\n"
            "    },\n"
            "    {\n"
            "      \"stt\": 72,\n"
            "      \"trichYeu\": \"Bản án hình sự số thẩm số 168/2024\",\n"
            "      \"tuToSo\": \"75-82\",\n"
            "      \"dacDiem\": \"Bản chính\",\n"
            "      \"doMat\": null,\n"
            "      \"ghiChu\": null\n"
            "    },\n"
            "    {\n"
            "      \"stt\": 80,\n"
            "      \"trichYeu\": \"Quyết định đưa người bị kết án đến nơi CHA\",\n"
            "      \"tuToSo\": 90,\n"
            "      \"dacDiem\": \"Bản trích sao\",\n"
            "      \"doMat\": null,\n"
            "      \"ghiChu\": null\n"
            "    }\n"
            "  ]\n"
            "}"
        )

    def process_document_stats_folder_ocr(self):
        folder_path = filedialog.askdirectory(
            title="Chọn thư mục chứa ảnh bảng 'Thống Kê Tài Liệu'",
            parent=self.master
        )
        if not folder_path:
            self._ocr_set_status("Hủy chọn thư mục.")
            return

        if not hasattr(self, 'ocr_api_url_entry') or not hasattr(self, 'ocr_model_entry'):
            messagebox.showerror("Lỗi cấu hình UI", "Các thành phần UI cho OCR chưa được khởi tạo đúng cách.", parent=self.master)
            return
        
        api_url = self.ocr_api_url_entry.get().strip()
        model = self.ocr_model_entry.get().strip()

        if not api_url:
            self._ocr_set_status("Lỗi: Vui lòng nhập URL của API OCR.", is_error=True)
            return

        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        if not image_files:
            messagebox.showinfo("Không có ảnh", f"Không tìm thấy file ảnh nào trong thư mục:\n{folder_path}", parent=self.master)
            self._ocr_set_status(f"Không có ảnh trong {os.path.basename(folder_path)}.")
            return

        self._ocr_set_status(f"Bắt đầu xử lý {len(image_files)} ảnh từ thư mục '{os.path.basename(folder_path)}'...")
        specific_prompt = self._get_document_stats_prompt()
        processed_count = 0
        error_count = 0
        # Thư mục output sẽ được xác định bởi _save_json_data_to_file là "thong_ke"
        # khi "danhSachTaiLieu" có trong JSON response.

        for i, image_name in enumerate(image_files):
            image_path = os.path.join(folder_path, image_name)
            self._ocr_set_status(f"Đang xử lý: {image_name} ({i + 1}/{len(image_files)})...")
            
            response_data = call_ocr_api_from_python(
                image_path=image_path, api_url=api_url, model=model if model else None, prompt=specific_prompt
            )

            if response_data is None or "error" in response_data:
                error_msg = response_data['error'] if response_data and "error" in response_data else "Lỗi không xác định từ API."
                print(f"Lỗi OCR file {image_name}: {error_msg}")
                error_count += 1
                continue

            # Xử lý response_data để trích xuất JSON thực sự từ trường 'description'
            # và chỉ giữ lại 'danhSachTaiLieu' theo yêu cầu.
            actual_data_to_save = None
            if isinstance(response_data, dict) and "description" in response_data:
                try:
                    description_content = response_data["description"]
                    # Loại bỏ markdown ```json ... ``` nếu có
                    clean_description_content = description_content.strip()
                    if clean_description_content.startswith("```json"):
                        clean_description_content = clean_description_content[7:].strip()
                    if clean_description_content.endswith("```"):
                        clean_description_content = clean_description_content[:-3].strip()
                    
                    inner_json_data = json.loads(clean_description_content)
                    
                    if isinstance(inner_json_data, dict) and "danhSachTaiLieu" in inner_json_data:
                        actual_data_to_save = {"danhSachTaiLieu": inner_json_data["danhSachTaiLieu"]}
                    else:
                        error_msg = f"Lỗi: 'danhSachTaiLieu' không tìm thấy trong JSON của 'description' cho file {image_name}."
                        print(error_msg)
                        self._ocr_set_status(error_msg, is_error=True)
                        error_count += 1
                        continue
                except json.JSONDecodeError as e:
                    error_msg = f"Lỗi giải mã JSON từ 'description' cho {image_name}: {e}. Nội dung: '{response_data.get('description', '')[:200]}...'"
                    print(error_msg)
                    self._ocr_set_status(error_msg, is_error=True)
                    error_count += 1
                    continue
                except Exception as e:
                    error_msg = f"Lỗi không xác định khi xử lý 'description' cho {image_name}: {e}"
                    print(error_msg)
                    self._ocr_set_status(error_msg, is_error=True)
                    error_count += 1
                    continue
            elif isinstance(response_data, dict) and "danhSachTaiLieu" in response_data:
                # Trường hợp API trả về JSON trực tiếp (không có 'description')
                actual_data_to_save = {"danhSachTaiLieu": response_data["danhSachTaiLieu"]}
            else:
                error_msg = f"Phản hồi API không có 'description' hoặc 'danhSachTaiLieu' hợp lệ cho {image_name}. Phản hồi: {str(response_data)[:200]}..."
                print(error_msg)
                self._ocr_set_status(error_msg, is_error=True)
                error_count += 1
                continue

            if actual_data_to_save is None: # Double check, should have been caught by continues
                error_msg = f"Lỗi: Không thể chuẩn bị dữ liệu để lưu cho {image_name}."
                print(error_msg)
                self._ocr_set_status(error_msg, is_error=True)
                error_count += 1
                continue

            saved_json_data = OCRAppSimple._save_json_data_to_file(
                None, 
                actual_data_to_save, # Sử dụng dữ liệu đã được xử lý
                image_path,
                self.ocr_json_output_dir, # default_json_output_dir, sẽ bị override thành "thong_ke"
                self._ocr_set_status, 
                self.master 
            )
            
            if saved_json_data:
                processed_count += 1
            else:
                error_count += 1
        
        final_status_msg = f"Hoàn tất xử lý thư mục. {processed_count} file thành công, {error_count} file lỗi."
        self._ocr_set_status(final_status_msg)
        messagebox.showinfo("Hoàn Tất OCR Thư Mục", 
                            f"{final_status_msg}\nKết quả (nếu có) được lưu trong thư mục con 'thong_ke'.", 
                            parent=self.master)


    def browse_image_ocr(self):
        from tkinter import filedialog 
        file_path = filedialog.askopenfilename(
            title="Chọn file ảnh cho OCR",
            filetypes=(("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png"), ("All files", "*.*"))
        )
        # Xóa nội dung JSON cũ khi chọn ảnh mới hoặc hủy
        if hasattr(self, 'ocr_json_display_text') and self.ocr_json_display_text:
            self.ocr_json_display_text.config(state=tk.NORMAL)
            self.ocr_json_display_text.delete(1.0, tk.END)
            self.ocr_json_display_text.config(state=tk.DISABLED)

        if file_path:
            self.ocr_full_selected_image_path = file_path
            parent_folder = os.path.basename(os.path.dirname(file_path))
            file_name = os.path.basename(file_path)
            display_path = os.path.join("...", parent_folder, file_name) if parent_folder else file_name
            if hasattr(self, 'ocr_selected_image_path_var'):
                self.ocr_selected_image_path_var.set(display_path) # Vẫn cập nhật biến này nếu có label ẩn dùng nó
            self._ocr_set_status(f"Đã chọn: {display_path}")
            self.submit_ocr_request_ocr() 
        else:
            if hasattr(self, 'ocr_selected_image_path_var'):
                self.ocr_selected_image_path_var.set("Chưa chọn ảnh nào.")
            self.ocr_full_selected_image_path = ""
            self._ocr_set_status("Sẵn sàng")

    def submit_ocr_request_ocr(self):
        actual_file_path = self.ocr_full_selected_image_path
        
        # Xóa nội dung JSON cũ trước khi thực hiện yêu cầu mới
        if hasattr(self, 'ocr_json_display_text') and self.ocr_json_display_text:
            self.ocr_json_display_text.config(state=tk.NORMAL)
            self.ocr_json_display_text.delete(1.0, tk.END)
            self.ocr_json_display_text.config(state=tk.DISABLED)

        if not hasattr(self, 'ocr_api_url_entry') or not hasattr(self, 'ocr_model_entry'):
            messagebox.showerror("Lỗi cấu hình UI", "Các thành phần UI cho OCR chưa được khởi tạo đúng cách trong Tab Trực Quan Hóa.", parent=self.master)
            return
        api_url = self.ocr_api_url_entry.get().strip()
        model = self.ocr_model_entry.get().strip()
        if not actual_file_path:
            self._ocr_set_status("Lỗi: Vui lòng chọn một file ảnh.", is_error=True)
            # messagebox.showerror("Lỗi OCR", "Vui lòng chọn một file ảnh.", parent=self.master) # _ocr_set_status đã show rồi
            return
        if not api_url:
            self._ocr_set_status("Lỗi: Vui lòng nhập URL của API OCR.", is_error=True)
            # messagebox.showerror("Lỗi OCR", "Vui lòng nhập URL của API OCR.", parent=self.master) # _ocr_set_status đã show rồi
            return

        json_prompt = OCRAppSimple.PROMPT_FOR_JSON_EXTRACTION 
        
        self._ocr_set_status(f"Đang xử lý ảnh: {os.path.basename(actual_file_path)}... Vui lòng đợi.")
        model_to_send = model if model else None
        
        response_data = call_ocr_api_from_python(
            image_path=actual_file_path, api_url=api_url, model=model_to_send, prompt=json_prompt
        )

        if response_data is None:
            self._ocr_set_status("Lỗi: Không nhận được phản hồi từ API OCR.", is_error=True)
            # messagebox.showerror("Lỗi API OCR", "Không nhận được phản hồi từ API hoặc có lỗi không xác định.", parent=self.master)
            return
        if "error" in response_data:
            error_msg = response_data['error']
            self._ocr_set_status(f"Lỗi từ API OCR: {error_msg}", is_error=True)
            # messagebox.showerror("Lỗi API OCR", f"Lỗi: {error_msg}", parent=self.master)
            return

        try:
            os.makedirs(self.ocr_json_output_dir, exist_ok=True)
            # _save_json_data_to_file giờ sẽ trả về dữ liệu JSON đã được parse (nếu thành công)
            # hoặc None nếu có lỗi trong quá trình parse hoặc lưu.
            saved_json_data = OCRAppSimple._save_json_data_to_file(
                None, response_data, actual_file_path, self.ocr_json_output_dir, 
                self._ocr_set_status, self.master
            )
            
            if saved_json_data and hasattr(self, 'ocr_json_display_text') and self.ocr_json_display_text:
                self.ocr_json_display_text.config(state=tk.NORMAL)
                self.ocr_json_display_text.delete(1.0, tk.END)
                # Định dạng JSON cho đẹp
                pretty_json = json.dumps(saved_json_data, indent=4, ensure_ascii=False)
                self.ocr_json_display_text.insert(tk.END, pretty_json)
                self.ocr_json_display_text.config(state=tk.DISABLED)
                self._ocr_set_status(f"OCR thành công. Kết quả JSON đã lưu và hiển thị.") # Cập nhật trạng thái
            elif not saved_json_data:
                # Lỗi đã được xử lý và thông báo bởi _save_json_data_to_file hoặc _ocr_set_status
                pass

        except Exception as e:
            self._ocr_set_status(f"Lỗi khi xử lý/lưu kết quả OCR: {e}", is_error=True)
            # messagebox.showerror("Lỗi OCR", f"Lỗi khi xử lý hoặc lưu kết quả OCR: {e}", parent=self.master)

    def open_search_window_ocr(self):
        os.makedirs(self.ocr_json_output_dir, exist_ok=True)
        if not hasattr(self, "ocr_search_win_instance") or not self.ocr_search_win_instance.winfo_exists():
            self.ocr_search_win_instance = OCRSearchWindow(self.master, self.ocr_json_output_dir)
            self.ocr_search_win_instance.grab_set() 
        else:
            self.ocr_search_win_instance.lift() 
            self.ocr_search_win_instance.focus_set()

    # --- PDF Viewer Tab related methods (adapted from pdf_viewer_app.PDFViewerApp) ---
    # Các widget pdf_viewer_current_file_label, pdf_viewer_extracted_text_widget, pdf_viewer_ocr_status_label
    # giờ đây được tạo và quản lý bởi ui_tab_visualize.py và gán vào self (app_instance)
    # nên các phương thức này sẽ hoạt động với các widget đó.
    def pdf_viewer_open_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file PDF",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")),
            parent=self.master
        )
        if not file_path:
            return
        
        if not hasattr(self, 'pdf_viewer_current_file_label'):
            messagebox.showerror("Lỗi cấu hình UI", "Label hiển thị file PDF chưa được khởi tạo trong Tab Trực Quan Hóa.", parent=self.master)
            return

        self.pdf_viewer_current_file_label.config(text=f"Đang mở: {os.path.basename(file_path)}")
        self.master.update_idletasks()

        if hasattr(self, 'pdf_viewer_extracted_text_widget') and self.pdf_viewer_extracted_text_widget:
            self.pdf_viewer_extracted_text_widget.config(state=tk.NORMAL)
            self.pdf_viewer_extracted_text_widget.delete(1.0, tk.END)
            self.pdf_viewer_extracted_text_widget.config(state=tk.DISABLED)

        if self.pdf_viewer_document:
            try:
                self.pdf_viewer_document.close()
            except Exception:
                pass 
            self.pdf_viewer_document = None
        
        try:
            self.pdf_viewer_document = fitz.open(file_path)
            self.pdf_viewer_current_file_path = file_path 
        except Exception as e:
            messagebox.showerror("Lỗi Mở PDF",
                                 f"Không thể mở file PDF: {os.path.basename(file_path)}\nLỗi: {e}",
                                 parent=self.master)
            self.pdf_viewer_reset_viewer_state()
            self.pdf_viewer_current_file_label.config(text="Lỗi khi mở file.")
            return

        if len(self.pdf_viewer_document) > 0:
            self.pdf_viewer_current_file_label.config(text=f"Đã mở: {os.path.basename(file_path)}")
            self._pdf_viewer_set_ocr_status(f"Sẵn sàng trích xuất từ {os.path.basename(file_path)} ({len(self.pdf_viewer_document)} trang).")
        else:
            messagebox.showinfo("Thông tin", "File PDF này không có trang nào.", parent=self.master)
            self.pdf_viewer_reset_viewer_state()
            self.pdf_viewer_current_file_label.config(text=f"File rỗng: {os.path.basename(file_path)}")

    def pdf_viewer_reset_viewer_state(self):
        if self.pdf_viewer_document:
            try:
                self.pdf_viewer_document.close()
            except Exception:
                pass
        self.pdf_viewer_document = None
        self.pdf_viewer_current_file_path = None
        if hasattr(self, 'pdf_viewer_current_file_label') and self.pdf_viewer_current_file_label:
            self.pdf_viewer_current_file_label.config(text="Chưa có file nào được mở.")
        if hasattr(self, 'pdf_viewer_extracted_text_widget') and self.pdf_viewer_extracted_text_widget:
            self.pdf_viewer_extracted_text_widget.config(state=tk.NORMAL)
            self.pdf_viewer_extracted_text_widget.delete(1.0, tk.END)
            self.pdf_viewer_extracted_text_widget.config(state=tk.DISABLED)
        self._pdf_viewer_set_ocr_status("Sẵn sàng.")

    def _pdf_viewer_set_ocr_status(self, message, is_error=False):
        if hasattr(self, 'pdf_viewer_ocr_status_label') and self.pdf_viewer_ocr_status_label:
            self.pdf_viewer_ocr_status_label.config(text=f"Trạng thái OCR: {message}", 
                                                    foreground="red" if is_error else "black")
            self.master.update_idletasks()
        else:
            print(f"DEBUG PDF OCR Status (widget not found): {message}")


    async def _process_text_with_ai_chat(self, text_to_process, page_number_for_prompt):
        if not hasattr(self, 'ai_chat_handler') or not hasattr(self.ai_chat_handler, '_call_chat_api'):
            print("⚠️ Lỗi: AIChatHandler hoặc _call_chat_api không sẵn sàng để xử lý văn bản PDF.")
            return f"[Văn bản gốc chưa qua AI xử lý do lỗi cấu hình] {text_to_process}"

        processing_prompt = (
            f"Đây là văn bản từ trang {page_number_for_prompt} của một tài liệu PDF. "
            "Vui lòng xử lý văn bản này và đảm bảo toàn bộ kết quả trả về bằng tiếng Việt.\n" 
            "Hướng dẫn xử lý:\n"
            "1. Tóm tắt nội dung chính trong khoảng 50-100 từ.\n"
            "2. Liệt kê các thực thể quan trọng (tên người, tổ chức, địa điểm) nếu có.\n"
            "3. Giữ nguyên các định dạng cơ bản nếu có thể.\n"
            "Văn bản cần xử lý:\n"
            "-------------------\n"
            f"{text_to_process}\n"
            "-------------------\n"
            "Kết quả xử lý (tiếng Việt):" 
        )
        
        self._pdf_viewer_set_ocr_status(f"Trang {page_number_for_prompt}: Đang gửi văn bản OCR đến AI Chat để xử lý...")
        processed_text = self.ai_chat_handler._call_chat_api(user_input_prompt=processing_prompt) 
        if processed_text.startswith("Lỗi:"): 
            return f"[Lỗi AI xử lý: {processed_text}] {text_to_process}" 
        return processed_text

    async def pdf_viewer_extract_text_ocr(self): 
        if not self.pdf_viewer_document:
            messagebox.showwarning("Chưa mở PDF", "Vui lòng mở một file PDF trước khi trích xuất văn bản.", parent=self.master)
            self._pdf_viewer_set_ocr_status("Lỗi: Chưa mở file PDF.", is_error=True)
            return
        
        if not hasattr(self, 'pdf_viewer_extracted_text_widget'):
            messagebox.showerror("Lỗi cấu hình UI", "Widget hiển thị text OCR PDF chưa được khởi tạo trong Tab Trực Quan Hóa.", parent=self.master)
            return

        total_pages_in_doc = len(self.pdf_viewer_document)
        if total_pages_in_doc == 0:
            messagebox.showinfo("Thông tin", "File PDF này không có trang nào để trích xuất.", parent=self.master)
            self._pdf_viewer_set_ocr_status("File PDF rỗng.", is_error=True)
            return

        self._pdf_viewer_set_ocr_status(f"Đang trích xuất văn bản từ {total_pages_in_doc} trang...")
        self.pdf_viewer_extracted_text_widget.config(state=tk.NORMAL)
        self.pdf_viewer_extracted_text_widget.delete(1.0, tk.END)
        
        all_pages_text_list = []
        combined_text_for_display = []
        any_ocr_error = False

        try:
            for page_num in range(total_pages_in_doc):
                self._pdf_viewer_set_ocr_status(f"Đang xử lý trang {page_num + 1}/{total_pages_in_doc}...")
                self.master.update_idletasks() 

                page_object = self.pdf_viewer_document.load_page(page_num)
                text_for_page = extract_text_from_image_page(page_object, language='vie')
                
                if "Lỗi:" in text_for_page:
                    any_ocr_error = True
                    processed_text_for_page = text_for_page 
                else:
                    processed_text_for_page = await self._process_text_with_ai_chat(text_for_page, page_num + 1)
                    if "[Lỗi AI xử lý:" in processed_text_for_page: 
                        any_ocr_error = True 
                
                all_pages_text_list.append({"page_number": page_num + 1, "original_ocr_text": text_for_page, "ai_processed_text": processed_text_for_page})
                combined_text_for_display.append(f"--- Trang {page_num + 1} (Kết quả sau khi AI xử lý) ---\n{processed_text_for_page}\n\n")

            self.pdf_viewer_extracted_text_widget.insert(tk.END, "".join(combined_text_for_display))
            
            if any_ocr_error:
                self._pdf_viewer_set_ocr_status(f"Hoàn tất trích xuất {total_pages_in_doc} trang (có lỗi ở một số trang).", is_error=True)
                messagebox.showwarning("Hoàn tất với lỗi", "Quá trình OCR hoàn tất, nhưng có lỗi xảy ra ở một số trang. Vui lòng kiểm tra kết quả.", parent=self.master)
            else:
                self._pdf_viewer_set_ocr_status(f"Hoàn tất trích xuất {total_pages_in_doc} trang.")
            
            self._save_pdf_ocr_result(all_pages_text_list, total_pages_in_doc)

        except Exception as e:
            error_msg = f"Lỗi trong quá trình OCR: {e}"
            self._pdf_viewer_set_ocr_status(error_msg, is_error=True)
            messagebox.showerror("Lỗi OCR", error_msg, parent=self.master)
        finally:
            self.pdf_viewer_extracted_text_widget.config(state=tk.DISABLED)

    def _save_pdf_ocr_result(self, pages_content_list, total_pages_processed):
        if not self.pdf_viewer_current_file_path: 
            return

        output_dir = self.pdf_ocr_json_output_dir 
        os.makedirs(output_dir, exist_ok=True)

        pdf_filename = os.path.basename(self.pdf_viewer_current_file_path)
        base_name_without_ext, _ = os.path.splitext(pdf_filename)
        
        json_filename = f"{base_name_without_ext}_ocr_result.json" 
        full_json_path = os.path.join(output_dir, json_filename)

        data_to_save = {
            "source_pdf": pdf_filename,
            "total_pages_processed": total_pages_processed,
            "pages": pages_content_list, 
            "extraction_timestamp": datetime.datetime.now().isoformat()
        }

        try:
            with open(full_json_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            print(f"✅ Kết quả OCR từ PDF đã lưu vào: {full_json_path}")
            self._pdf_viewer_set_ocr_status(f"Đã lưu kết quả vào {json_filename}.")
            self._pdf_viewer_set_ocr_status(f"Đang phân tách file {json_filename} theo tiêu đề...")
            self._split_and_merge_pdf_ocr_result(full_json_path)
        except Exception as e:
            error_msg = f"Lỗi khi lưu file JSON OCR từ PDF: {e}"
            print(f"❌ {error_msg}")
            self._pdf_viewer_set_ocr_status(error_msg, is_error=True)
            messagebox.showerror("Lỗi Lưu File", error_msg, parent=self.master)

    def _split_and_merge_pdf_ocr_result(self, json_path):
        output_dir = self.pdf_split_output_dir
        os.makedirs(output_dir, exist_ok=True)

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._pdf_viewer_set_ocr_status(f"Đã tải file JSON: {os.path.basename(json_path)} để phân tách.")
        except FileNotFoundError:
            msg = f"Lỗi phân tách: Không tìm thấy file {os.path.basename(json_path)}"
            self._pdf_viewer_set_ocr_status(msg, is_error=True)
            messagebox.showerror("Lỗi Phân Tách PDF JSON", msg, parent=self.master)
            return
        except json.JSONDecodeError:
            msg = f"Lỗi phân tách: File {os.path.basename(json_path)} không phải JSON hợp lệ."
            self._pdf_viewer_set_ocr_status(msg, is_error=True)
            messagebox.showerror("Lỗi Phân Tách PDF JSON", msg, parent=self.master)
            return

        doc_keywords = {
            "Quyết định lập hồ sơ": "QUYÉT ĐỊNH LẬP HỎ SƠ PHAM NHÂN",
            "Danh bản phạm nhân": "DANH BẢN PHẠM NHÂN",
            "Chỉ bản phạm nhân": "CHỈ BẢN PHẠM NHÂN",
            "Lệnh bắt bị can để tạm giam": "LỆNH BẮT BỊ CAN ĐỀ TẠM GIAM",
            "Quyết định phê chuẩn": "QUYẾT ĐỊNH PHÊ CHUẢN LẬP HỖ SƠ PHẠM NHÂN",
            "Biên bản bắt bị can để tạm giam": "BIÊN BẢN BẮT BỊ CAN ĐỀ TẠM GIAM"
        }

        page_groups = {}
        current_group_key = None

        for page in data.get('pages', []):
            text = page.get('original_ocr_text', '') 
            for key, title_keyword in doc_keywords.items():
                if title_keyword in text:
                    current_group_key = key
                    if current_group_key not in page_groups:
                        page_groups[current_group_key] = []
                    break 
            
            if current_group_key:
                page_groups[current_group_key].append(page)
            else:
                if "uncategorized" not in page_groups:
                    page_groups["uncategorized"] = []
                page_groups["uncategorized"].append(page)

        self._pdf_viewer_set_ocr_status(f"Đã xác định {len(page_groups)} mục tài liệu.")

        danh_ban_key = "Danh bản phạm nhân"
        chi_ban_key = "Chỉ bản phạm nhân"
        if danh_ban_key in page_groups and chi_ban_key in page_groups:
            self._pdf_viewer_set_ocr_status(f"Đang gộp '{doc_keywords[danh_ban_key]}' và '{doc_keywords[chi_ban_key]}'.")
            merged_pages = page_groups[danh_ban_key] + page_groups[chi_ban_key]
            merged_key = "Danh bản + Chỉ bản"
            page_groups[merged_key] = merged_pages
            del page_groups[danh_ban_key]
            del page_groups[chi_ban_key]

        num_files_created = 0
        for group_key, pages_list in page_groups.items():
            if group_key == "uncategorized" and not pages_list:
                continue

            output_filename = os.path.join(output_dir, f"{group_key}.json")
            document_title_for_json = doc_keywords.get(group_key, "Uncategorized Document")
            if group_key == "Danh bản + Chỉ bản":
                 document_title_for_json = "DANH BẢN + CHỈ BẢN PHẠM NHÂN"

            output_data = {
                "source_pdf_ocr_file": os.path.basename(json_path),
                "document_title": document_title_for_json,
                "total_pages_in_section": len(pages_list),
                "pages": pages_list
            }
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
            num_files_created +=1
            print(f"✅ Đã tạo file JSON phân tách: {output_filename}")

        self._pdf_viewer_set_ocr_status(f"Hoàn tất phân tách. Đã tạo {num_files_created} file trong '{output_dir}'.")
        messagebox.showinfo("Hoàn Tất Phân Tách", f"Đã phân tách và lưu {num_files_created} tài liệu vào thư mục:\n{os.path.abspath(output_dir)}", parent=self.master)
