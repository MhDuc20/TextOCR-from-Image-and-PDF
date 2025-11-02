# pdf_viewer_app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox # scrolledtext không còn dùng
import os
import fitz  # PyMuPDF
from PIL import Image, ImageTk # Pillow

class PDFViewerApp:
    def __init__(self, master):
        self.master = master
        master.title("Trình xem PDF trực quan")
        master.geometry("800x700") # Tăng chiều cao một chút cho thanh điều hướng

        self.pdf_document = None
        self.current_page_num = 0  # 0-indexed
        self.total_pages = 0
        self.tk_image = None  # Giữ tham chiếu đến PhotoImage

        # --- UI Elements ---
        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame cho nút và label file
        top_frame = ttk.Frame(self.main_frame) # Sửa lỗi thụt lề nếu có
        top_frame.pack(fill=tk.X, pady=(0, 10))

        self.open_button = ttk.Button(top_frame, text="Mở File PDF...", command=self.open_pdf_file)
        self.open_button.pack(side=tk.LEFT, padx=(0, 10))

        self.current_file_label = ttk.Label(top_frame, text="Chưa có file nào được mở.")
        self.current_file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Frame cho Canvas (hiển thị PDF) và thanh cuộn
        canvas_frame = ttk.Frame(self.main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.canvas = tk.Canvas(canvas_frame, bg="lightgrey", relief=tk.SOLID, borderwidth=1)
        
        self.v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame cho các nút điều hướng trang
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.pack(fill=tk.X, pady=(5, 0))

        self.prev_button = ttk.Button(nav_frame, text="< Trang Trước", command=self.go_to_previous_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.page_label = ttk.Label(nav_frame, text="Trang: - / -")
        self.page_label.pack(side=tk.LEFT, padx=5, expand=True)

        self.next_button = ttk.Button(nav_frame, text="Trang Tiếp >", command=self.go_to_next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

    def open_pdf_file(self):
        """Mở hộp thoại để chọn file PDF và hiển thị trang đầu tiên."""
        file_path = filedialog.askopenfilename(
            title="Chọn file PDF",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        if not file_path:
            return

        self.current_file_label.config(text=f"Đang mở: {os.path.basename(file_path)}")
        self.master.update_idletasks()

        if self.pdf_document:
            try:
                self.pdf_document.close()
            except Exception:
                pass # Bỏ qua lỗi nếu không đóng được
            self.pdf_document = None
        
        self.canvas.delete("all") # Xóa nội dung canvas cũ
        self.tk_image = None # Xóa tham chiếu ảnh cũ

        try:
            self.pdf_document = fitz.open(file_path)
        except Exception as e:
            messagebox.showerror("Lỗi Mở PDF",
                                 f"Không thể mở file PDF: {os.path.basename(file_path)}\nLỗi: {e}",
                                 parent=self.master)
            self.reset_viewer_state()
            self.current_file_label.config(text="Lỗi khi mở file.")
            return

        self.total_pages = len(self.pdf_document)
        if self.total_pages > 0:
            self.current_page_num = 0
            self.display_page(self.current_page_num)
            self.current_file_label.config(text=f"Đã mở: {os.path.basename(file_path)}")
        else:
            messagebox.showinfo("Thông tin", "File PDF này không có trang nào.", parent=self.master)
            self.reset_viewer_state()
            self.current_file_label.config(text=f"File rỗng: {os.path.basename(file_path)}")
        
        self.update_navigation_controls()

    def reset_viewer_state(self):
        """Đặt lại trạng thái của trình xem."""
        if self.pdf_document:
            try:
                self.pdf_document.close()
            except Exception:
                pass
        self.pdf_document = None
        self.current_page_num = 0
        self.total_pages = 0
        self.canvas.delete("all")
        self.tk_image = None
        self.page_label.config(text="Trang: - / -")
        # self.current_file_label.config(text="Chưa có file nào được mở.") # Để open_pdf_file tự quản lý
        self.update_navigation_controls()


    def display_page(self, page_number):
        if not self.pdf_document or not (0 <= page_number < self.total_pages):
            return

        self.canvas.delete("all") # Xóa trang hiện tại trên canvas
        page = self.pdf_document.load_page(page_number)

        zoom_matrix = fitz.Matrix(1.5, 1.5) 
        pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)

        img_mode = "RGB"
        try:
            img = Image.frombytes(img_mode, [pix.width, pix.height], pix.samples)
        except ValueError:
            try:
                pix_rgba = page.get_pixmap(matrix=zoom_matrix, alpha=True)
                img = Image.frombytes("RGBA", [pix_rgba.width, pix_rgba.height], pix_rgba.samples)
            except Exception as e:
                 messagebox.showerror("Lỗi Hiển Thị Trang", f"Không thể render trang PDF.\nLỗi: {e}", parent=self.master)
                 return

        self.tk_image = ImageTk.PhotoImage(img)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        self.current_page_num = page_number
        self.page_label.config(text=f"Trang: {self.current_page_num + 1} / {self.total_pages}")
        self.update_navigation_controls()

    def go_to_previous_page(self):
        if self.pdf_document and self.current_page_num > 0:
            self.display_page(self.current_page_num - 1)

    def go_to_next_page(self):
        if self.pdf_document and self.current_page_num < self.total_pages - 1:
            self.display_page(self.current_page_num + 1)

    def update_navigation_controls(self):
        """Cập nhật trạng thái của các nút điều hướng."""
        if self.pdf_document and self.total_pages > 0:
            self.prev_button.config(state=tk.NORMAL if self.current_page_num > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.current_page_num < self.total_pages - 1 else tk.DISABLED)
        else:
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.page_label.config(text="Trang: - / -")

    def on_close(self):
        """Xử lý khi đóng cửa sổ."""
        if self.pdf_document:
            try:
                self.pdf_document.close()
            except Exception:
                pass
        self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = PDFViewerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close) # Xử lý sự kiện đóng cửa sổ
    root.mainloop()
