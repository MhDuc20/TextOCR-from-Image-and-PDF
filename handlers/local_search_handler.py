# handlers/local_search_handler.py
import tkinter as tk

class LocalSearchHandler:
    def __init__(self, app_instance):
        self.app = app_instance

    def perform_local_search(self):
        """Performs a local search based on the user's query."""
        if not hasattr(self.app, 'local_search_entry') or not hasattr(self.app, 'local_search_results_text'):
            return

        query = self.app.local_search_entry.get().strip().lower()
        results_text_widget = self.app.local_search_results_text
        results_text_widget.config(state=tk.NORMAL)
        results_text_widget.delete("1.0", tk.END)

        if not query:
            results_text_widget.insert(tk.END, "Vui lòng nhập từ khóa để tìm kiếm.")
            results_text_widget.config(state=tk.DISABLED)
            return

        results_found = False
        # Search in vb_den_data
        for vb in self.app.vb_den_data:
            if (query in vb.get("so_ky_hieu", "").lower() or
                query in vb.get("trich_yeu", "").lower() or
                query in vb.get("noi_dung", "").lower()):
                results_text_widget.insert(tk.END, "[VĂN BẢN ĐẾN]\n", ("header_bold"))
                results_text_widget.insert(tk.END, f"  Số ký hiệu: {vb.get('so_ky_hieu', 'N/A')}\n")
                results_text_widget.insert(tk.END, f"  Trích yếu: {vb.get('trich_yeu', 'N/A')}\n")
                results_text_widget.insert(tk.END, f"  Ngày ban hành: {vb.get('ngay_ban_hanh', 'N/A')}\n---\n\n")
                results_found = True
        
        # Search in vb_di_data
        for vb in self.app.vb_di_data:
            if (query in vb.get("so_ky_hieu", "").lower() or
                query in vb.get("trich_yeu", "").lower() or
                query in vb.get("noi_dung", "").lower()):
                results_text_widget.insert(tk.END, "[VĂN BẢN ĐI]\n", ("header_bold"))
                results_text_widget.insert(tk.END, f"  Số ký hiệu: {vb.get('so_ky_hieu', 'N/A')}\n")
                results_text_widget.insert(tk.END, f"  Trích yếu: {vb.get('trich_yeu', 'N/A')}\n")
                results_text_widget.insert(tk.END, f"  Ngày ban hành: {vb.get('ngay_ban_hanh', 'N/A')}\n---\n\n")
                results_found = True
        
        # Search in all_available_question_objects (includes AI-added ones)
        for ch in self.app.all_available_question_objects:
            question_text_lower = ch.get("question", "").lower()
            answer_text_lower = ch.get("answer", "").lower()
            if query in question_text_lower or query in answer_text_lower:
                results_text_widget.insert(tk.END, "[CÂU HỎI GỢI Ý]\n", ("header_bold"))
                results_text_widget.insert(tk.END, f"  Câu hỏi: {ch.get('question', 'N/A')}\n")
                results_text_widget.insert(tk.END, f"  Trả lời: {ch.get('answer', 'N/A')}\n---\n\n")
                results_found = True
        
        if not results_found:
            results_text_widget.insert(tk.END, f"Không tìm thấy kết quả nào cho '{query}' trong dữ liệu.")
        
        results_text_widget.config(state=tk.DISABLED)
