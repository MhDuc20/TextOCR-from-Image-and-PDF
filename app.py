# app.py
import tkinter as tk
from tkinter import ttk
import sys
from app_gui import SimpleQuestionViewerApp

if __name__ == '__main__':
    root = tk.Tk()
    app = SimpleQuestionViewerApp(root) # DataManager is initialized within SimpleQuestionViewerApp

    # Check if data loading failed (DataManager sets these on app instance)
    # Access filenames from the DataManager instance for the error message
    dm = app.data_manager
    if not app.cau_hoi_data and not app.vb_den_data and not app.vb_di_data:
        root.withdraw()
        
        error_root = tk.Toplevel()
        error_root.title("Lỗi Tải Dữ Liệu")
        error_root.geometry("450x180")
        
        error_message = "Không thể tải bất kỳ dữ liệu nào.\n" \
                        "Vui lòng kiểm tra các file JSON sau trong cùng thư mục:\n" \
                        f"- {dm.cau_hoi_filename}\n" \
                        f"- {dm.van_ban_den_filename}\n" \
                        f"- {dm.van_ban_di_filename}\n\n" \
                        "Hãy đảm bảo chúng tồn tại và có định dạng đúng.\n" \
                        "Ứng dụng sẽ thoát khi bạn đóng thông báo này."
        
        ttk.Label(error_root, text=error_message, padding=20, justify=tk.LEFT).pack(expand=True, fill=tk.BOTH)
        
        def close_all_and_exit():
            error_root.destroy()
            if root.winfo_exists():
                root.destroy()
            sys.exit()

        error_root.protocol("WM_DELETE_WINDOW", close_all_and_exit)
        ttk.Button(error_root, text="Đóng và Thoát", command=close_all_and_exit).pack(pady=10)
        
        error_root.mainloop()
    else:
        root.mainloop()
