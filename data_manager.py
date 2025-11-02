# data_manager.py
import json
import os
from tkinter import messagebox

class DataManager:
    def __init__(self, app_instance):
        self.app = app_instance
        
        # Get the directory where THIS script file is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Use absolute paths for JSON files
        self.cau_hoi_filename = os.path.join(self.script_dir, "cau_hoi_lien_quan.json")
        self.van_ban_den_filename = os.path.join(self.script_dir, "van_ban_den.json")
        self.van_ban_di_filename = os.path.join(self.script_dir, "van_ban_di.json")
        
        # Debug: Print the paths being used
        print(f"DataManager initialized with script directory: {self.script_dir}")
        print(f"Looking for JSON files:")
        print(f"  - {self.cau_hoi_filename}")
        print(f"  - {self.van_ban_den_filename}")
        print(f"  - {self.van_ban_di_filename}")
        
        # Check if files exist
        print(f"File existence check:")
        print(f"  - cau_hoi_lien_quan.json: {'✅ EXISTS' if os.path.exists(self.cau_hoi_filename) else '❌ NOT FOUND'}")
        print(f"  - van_ban_den.json: {'✅ EXISTS' if os.path.exists(self.van_ban_den_filename) else '❌ NOT FOUND'}")
        print(f"  - van_ban_di.json: {'✅ EXISTS' if os.path.exists(self.van_ban_di_filename) else '❌ NOT FOUND'}")

        # Initialize data attributes on the app instance
        self.app.cau_hoi_data = []
        self.app.vb_den_data = []
        self.app.vb_di_data = []
        # This list will hold all questions, including those added by AI during the session
        self.app.all_available_question_objects = []
        # This list will store the original indices of questions currently shown in the listbox (after filtering)
        self.app.current_displaying_question_indices_in_all = []

    def load_all_data(self):
        """Loads all necessary data for the application."""
        print("🔄 Starting data loading process...")
        
        self.app.cau_hoi_data = self._load_json_file(self.cau_hoi_filename, "câu hỏi gợi ý")
        self.app.vb_den_data = self._load_json_file(self.van_ban_den_filename, "văn bản đến")
        self.app.vb_di_data = self._load_json_file(self.van_ban_di_filename, "văn bản đi")

        # Initialize all_available_question_objects with data from cau_hoi_data
        # This list will be augmented by AI-generated questions later
        if self.app.cau_hoi_data:
            self.app.all_available_question_objects.extend(list(self.app.cau_hoi_data)) # Use list() for a shallow copy if modification is complex
        
        print(f"📊 Data loading completed:")
        print(f"   - Questions loaded: {len(self.app.cau_hoi_data)}")
        print(f"   - Incoming documents loaded: {len(self.app.vb_den_data)}")
        print(f"   - Outgoing documents loaded: {len(self.app.vb_di_data)}")

    def _load_json_file(self, full_file_path, data_type_name):
        """Load JSON file using absolute path"""
        data = []
        filename = os.path.basename(full_file_path)
        
        try:
            with open(full_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data:
                print(f"✅ Đã tải {len(data)} {data_type_name} từ '{filename}'.")
            else:
                print(f"⚠️ File '{filename}' rỗng hoặc không chứa dữ liệu {data_type_name} hợp lệ.")
        except FileNotFoundError:
            print(f"❌ LỖI: Không tìm thấy file '{filename}' tại đường dẫn: {full_file_path}")
            print(f"📁 Thư mục hiện tại: {os.getcwd()}")
            print(f"📁 Thư mục script: {self.script_dir}")
            
            # Try to create default file
            if self._create_default_file(full_file_path, data_type_name):
                print(f"✅ Đã tạo file mẫu '{filename}'. Đang tải lại...")
                return self._load_json_file(full_file_path, data_type_name)
            
        except json.JSONDecodeError as e:
            print(f"❌ LỖI: Lỗi khi đọc file JSON '{filename}': {e}")
            messagebox.showerror("Lỗi Tải Dữ Liệu", f"Lỗi khi đọc file JSON '{filename}'. Vui lòng kiểm tra định dạng file.\n\nLỗi: {e}")
        except Exception as e:
            print(f"❌ LỖI: Lỗi không xác định khi tải '{filename}': {e}")
            messagebox.showerror("Lỗi Tải Dữ Liệu", f"Lỗi không xác định khi tải '{filename}':\n{e}")
        
        return data

    def _create_default_file(self, full_file_path, data_type_name):
        """Create a default JSON file with sample data"""
        filename = os.path.basename(full_file_path)
        
        try:
            # Create default data based on file type
            if "cau_hoi" in filename:
                default_data = [
                    {
                        "id": 1,
                        "question": "Câu hỏi mẫu 1?",
                        "answer": "Đây là câu trả lời mẫu cho câu hỏi 1.",
                        "category": "Tổng quát",
                        "keywords": ["mẫu", "demo"]
                    },
                    {
                        "id": 2,
                        "question": "Câu hỏi mẫu 2?",
                        "answer": "Đây là câu trả lời mẫu cho câu hỏi 2.",
                        "category": "Hướng dẫn",
                        "keywords": ["hướng dẫn", "demo"]
                    }
                ]
            elif "van_ban_den" in filename:
                default_data = [
                    {
                        "id": 1,
                        "title": "Văn bản đến mẫu 1",
                        "content": "Nội dung văn bản đến mẫu số 1.",
                        "date": "2024-01-01",
                        "sender": "Đơn vị gửi mẫu",
                        "type": "Công văn"
                    }
                ]
            elif "van_ban_di" in filename:
                default_data = [
                    {
                        "id": 1,
                        "title": "Văn bản đi mẫu 1",
                        "content": "Nội dung văn bản đi mẫu số 1.",
                        "date": "2024-01-01",
                        "recipient": "Đơn vị nhận mẫu",
                        "type": "Công văn"
                    }
                ]
            else:
                default_data = []
            
            # Write the default data to file
            with open(full_file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
            
            print(f"✅ Đã tạo file mẫu '{filename}' với {len(default_data)} mục dữ liệu.")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi tạo file mẫu '{filename}': {e}")
            return False

    def save_cau_hoi_data(self):
        """Saves self.app.cau_hoi_data to its JSON file."""
        if not hasattr(self.app, 'cau_hoi_data'):
            print("❌ Lỗi: Thuộc tính cau_hoi_data không tồn tại trong app_instance.")
            return False
        try:
            with open(self.cau_hoi_filename, 'w', encoding='utf-8') as f:
                json.dump(self.app.cau_hoi_data, f, ensure_ascii=False, indent=4)
            print(f"✅ Đã cập nhật file '{os.path.basename(self.cau_hoi_filename)}'.")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi lưu file '{os.path.basename(self.cau_hoi_filename)}': {e}")
            messagebox.showerror("Lỗi Lưu File", f"Không thể lưu cập nhật vào file câu hỏi gợi ý:\n{e}")
            return False

    def get_next_question_id(self):
        """Gets the next available ID for a new question based on self.app.cau_hoi_data."""
        if not hasattr(self.app, 'cau_hoi_data') or not self.app.cau_hoi_data:
            return 1
        max_id = 0
        for item in self.app.cau_hoi_data:
            if isinstance(item.get("id"), int) and item.get("id") > max_id:
                max_id = item.get("id")
        return max_id + 1