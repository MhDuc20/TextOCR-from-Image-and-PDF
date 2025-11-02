# handlers/available_questions_handler.py
import tkinter as tk
from tkinter import ttk, messagebox 
import threading
import json
import re

class AvailableQuestionsHandler:
    def __init__(self, app_instance):
        self.app = app_instance
        self.data_manager = self.app.data_manager
        # self.ai_service is removed as local AI generation is no longer used here.

    def filter_available_questions(self, event=None):
        if not hasattr(self.app, 'all_available_question_objects') or \
           not hasattr(self.app, 'available_questions_listbox') or \
           not hasattr(self.app, 'available_questions_search_entry'):
            return

        query = self.app.available_questions_search_entry.get().strip().lower()
        
        self.app.available_questions_listbox.unbind("<<ListboxSelect>>")
        self.app.available_questions_listbox.delete(0, tk.END)
        self._clear_available_question_details()
        self.app.current_displaying_question_indices_in_all = []

        items_to_display_with_original_indices = []

        if self.app.all_available_question_objects:
            for original_index, q_obj in enumerate(self.app.all_available_question_objects):
                question_text = q_obj.get("question", "").lower()
                if not query or query in question_text: 
                    items_to_display_with_original_indices.append((q_obj, original_index))
        
        if not self.app.all_available_question_objects:
            self.app.available_questions_listbox.insert(tk.END, "Không có câu hỏi gợi ý nào được tải.")
            self.app.available_questions_listbox.config(state=tk.DISABLED)
        elif not items_to_display_with_original_indices: 
            self.app.available_questions_listbox.insert(tk.END, "Không tìm thấy câu hỏi nào khớp với tìm kiếm.")
            self.app.available_questions_listbox.config(state=tk.DISABLED)
        else:
            for display_index, (q_obj, original_idx) in enumerate(items_to_display_with_original_indices):
                listbox_item_text = f"{display_index + 1}. {q_obj.get('question', 'Lỗi: Câu hỏi không có nội dung')}"
                self.app.available_questions_listbox.insert(tk.END, listbox_item_text)
                self.app.current_displaying_question_indices_in_all.append(original_idx)
            self.app.available_questions_listbox.config(state=tk.NORMAL)

        self.app.available_questions_listbox.bind("<<ListboxSelect>>", self.app.on_available_question_select)


    def on_available_question_select(self, event=None):
        if not hasattr(self.app, 'available_questions_listbox') or \
           not hasattr(self.app, 'available_detail_description_text'):
            return

        if self.app.available_questions_listbox.cget('state') == tk.DISABLED or \
           not self.app.available_questions_listbox.curselection():
            self._clear_available_question_details()
            return
        
        try:
            selected_listbox_index = self.app.available_questions_listbox.curselection()[0]
        except IndexError:
            self._clear_available_question_details()
            return

        if not (0 <= selected_listbox_index < len(self.app.current_displaying_question_indices_in_all)):
            self._clear_available_question_details()
            return

        original_object_index = self.app.current_displaying_question_indices_in_all[selected_listbox_index]
            
        if not (0 <= original_object_index < len(self.app.all_available_question_objects)):
            self._clear_available_question_details()
            return
        
        selected_question_obj = self.app.all_available_question_objects[original_object_index]
        answer_text = selected_question_obj.get("answer", "N/A")

        self.app.available_detail_description_text.config(state=tk.NORMAL)
        self.app.available_detail_description_text.delete("1.0", tk.END)
        self.app.available_detail_description_text.insert(tk.END, answer_text)
        self.app.available_detail_description_text.config(state=tk.DISABLED)

    def _clear_available_question_details(self):
        if hasattr(self.app, 'available_detail_description_text') and self.app.available_detail_description_text:
            self.app.available_detail_description_text.config(state=tk.NORMAL)
            self.app.available_detail_description_text.delete("1.0", tk.END)
            self.app.available_detail_description_text.config(state=tk.DISABLED)

    def generate_new_questions_with_ai(self):
        """
        Initiates the process of generating new questions using the Bot API.
        """
        if not self.app.vb_den_data and not self.app.vb_di_data:
            messagebox.showwarning("Thiếu Dữ Liệu", "Không có dữ liệu văn bản đến hoặc văn bản đi để Bot API tạo câu hỏi.")
            return

        if not hasattr(self.app, 'ai_chat_handler') or not hasattr(self.app.ai_chat_handler, '_call_chat_api'):
            messagebox.showerror("Lỗi Cấu Hình", "AIChatHandler hoặc phương thức gọi API không sẵn sàng.")
            return

        # Disable button and show status
        add_button_widget = getattr(self.app, 'add_questions_ai_button', None)
        if add_button_widget:
            add_button_widget.config(state=tk.DISABLED)
        
        status_label_widget = getattr(self.app, 'ai_question_status_label', None)
        if status_label_widget:
            status_label_widget.config(text="Bot (API) đang chuẩn bị tạo câu hỏi...")

        thread = threading.Thread(target=self._generation_task_with_api, daemon=True)
        thread.start()

    def _build_context_for_question_generation(self):
        """Builds context from local data for the API to generate questions."""
        context_parts = ["Dưới đây là một số tài liệu văn bản được cung cấp:"]
        MAX_ITEMS_PER_SOURCE = 2 # Limit items to keep prompt manageable
        MAX_CONTENT_SNIPPET_LENGTH = 300 # Limit content length per item

        # Văn bản đến
        if hasattr(self.app, 'vb_den_data') and self.app.vb_den_data:
            context_parts.append("\n--- VĂN BẢN ĐẾN (TÓM TẮT) ---")
            for i, vb in enumerate(self.app.vb_den_data[:MAX_ITEMS_PER_SOURCE]):
                trich_yeu = vb.get('trich_yeu', 'N/A')
                noi_dung_snippet = str(vb.get('noi_dung', ''))[:MAX_CONTENT_SNIPPET_LENGTH]
                if len(vb.get('noi_dung', '')) > MAX_CONTENT_SNIPPET_LENGTH:
                    noi_dung_snippet += "..."
                context_parts.append(
                    f"[VB Đến {i+1}] Số ký hiệu: {vb.get('so_ky_hieu', 'N/A')}, "
                    f"Trích yếu: {trich_yeu}, Nội dung tóm tắt: {noi_dung_snippet}"
                )

        # Văn bản đi
        if hasattr(self.app, 'vb_di_data') and self.app.vb_di_data:
            context_parts.append("\n--- VĂN BẢN ĐI (TÓM TẮT) ---")
            for i, vb in enumerate(self.app.vb_di_data[:MAX_ITEMS_PER_SOURCE]):
                trich_yeu = vb.get('trich_yeu', 'N/A')
                noi_dung_snippet = str(vb.get('noi_dung', ''))[:MAX_CONTENT_SNIPPET_LENGTH]
                if len(vb.get('noi_dung', '')) > MAX_CONTENT_SNIPPET_LENGTH:
                    noi_dung_snippet += "..."
                context_parts.append(
                    f"[VB Đi {i+1}] Số ký hiệu: {vb.get('so_ky_hieu', 'N/A')}, "
                    f"Trích yếu: {trich_yeu}, Nội dung tóm tắt: {noi_dung_snippet}"
                )
        
        full_context = "\n".join(context_parts)
        MAX_CONTEXT_FOR_GEN_LENGTH = 3500 # Shorter than chat context, API might have stricter limits for generation
        if len(full_context) > MAX_CONTEXT_FOR_GEN_LENGTH:
            full_context = full_context[:MAX_CONTEXT_FOR_GEN_LENGTH] + "\n... (dữ liệu đã được rút gọn)"
        return full_context

    def _generation_task_with_api(self):
        status_label_widget = getattr(self.app, 'ai_question_status_label', None)
        add_button_widget = getattr(self.app, 'add_questions_ai_button', None)

        def update_status(text):
            if status_label_widget and status_label_widget.winfo_exists():
                self.app.master.after(0, lambda: status_label_widget.config(text=text))
        
        def re_enable_button():
            if add_button_widget and add_button_widget.winfo_exists():
                self.app.master.after(0, lambda: add_button_widget.config(state=tk.NORMAL))

        try:
            update_status("Bot (API) đang lấy ngữ cảnh...")
            context_data = self._build_context_for_question_generation()
            if not context_data.strip() or "Dưới đây là một số tài liệu văn bản được cung cấp:" == context_data.strip() :
                 update_status("Lỗi: Không có đủ dữ liệu để tạo câu hỏi.")
                 self.app.master.after(0, lambda: messagebox.showerror("Lỗi Dữ Liệu", "Không thể xây dựng ngữ cảnh từ dữ liệu hiện có."))
                 re_enable_button()
                 return

            generation_prompt = (
                f"{context_data}\n\n"
                f"--- YÊU CẦU ---\n"
                f"Dựa vào các tài liệu văn bản đã cung cấp ở trên, hãy tạo ra 2 đến 3 câu hỏi thường gặp (FAQ) "
                f"về các nội dung chính hoặc các vấn đề có thể phát sinh từ các văn bản này. "
                f"Mỗi câu hỏi nên đi kèm với một câu trả lời ngắn gọn, súc tích, dựa trên thông tin từ tài liệu. "
                f"Định dạng kết quả đầu ra PHẢI LÀ một danh sách JSON hợp lệ, trong đó mỗi phần tử là một đối tượng có hai khóa: \"question\" và \"answer\".\n"
                f"Ví dụ JSON: [{{ \"question\": \"Nội dung chính của văn bản X là gì?\", \"answer\": \"Văn bản X đề cập đến việc A và B.\"}}]\n"
                f"QUAN TRỌNG: Chỉ trả về DUY NHẤT danh sách JSON, không có bất kỳ văn bản giới thiệu, giải thích, hay ghi chú nào khác bao quanh nó."
                f"\n\nJSON Output:"
            )
            
            update_status("Bot (API) đang tạo câu hỏi...")
            api_response_str = self.app.ai_chat_handler._call_chat_api(generation_prompt)

            if api_response_str.startswith("Lỗi:"):
                self.app.master.after(0, lambda: messagebox.showerror("Lỗi API", api_response_str))
                update_status(f"Lỗi API: {api_response_str[:50]}...")
            else:
                newly_added_count = self._process_api_generated_questions(api_response_str)
                if newly_added_count > 0:
                    update_status(f"Đã thêm {newly_added_count} câu hỏi từ Bot (API).")
                else: # No new questions added, could be parsing error or no valid Q&As
                    if not (hasattr(self.app, '_last_gen_error_shown') and self.app._last_gen_error_shown): # Avoid multiple popups for same attempt
                        update_status("Bot (API) không tạo được câu hỏi hợp lệ.")
        except Exception as e:
            error_msg = f"Lỗi không mong muốn khi tạo câu hỏi: {e}"
            print(f"❌ {error_msg}")
            self.app.master.after(0, lambda: messagebox.showerror("Lỗi Hệ Thống", error_msg))
            update_status("Lỗi hệ thống khi tạo câu hỏi.")
        finally:
            re_enable_button()
            if status_label_widget and status_label_widget.winfo_exists() and \
               ("Lỗi" not in status_label_widget.cget("text") or "đang tải" in status_label_widget.cget("text")): # Don't clear error messages immediately
                 self.app.master.after(6000, lambda: status_label_widget.config(text="") if status_label_widget and status_label_widget.winfo_exists() else None)
            self.app._last_gen_error_shown = False # Reset flag

    def _process_api_generated_questions(self, api_response_str):
        newly_added_count = 0
        self.app._last_gen_error_shown = False # Flag to prevent multiple popups for parsing errors
        try:
            # Attempt to extract JSON from ```json ... ``` or directly parse
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", api_response_str, re.IGNORECASE)
            if json_match:
                json_str = json_match.group(1).strip()
            else: # If no markdown block, assume the response is direct JSON or needs cleaning
                first_bracket = api_response_str.find('[')
                last_bracket = api_response_str.rfind(']')
                if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
                    json_str = api_response_str[first_bracket : last_bracket+1]
                else:
                    json_str = api_response_str # Hope for the best

            generated_items = json.loads(json_str)
            if not isinstance(generated_items, list):
                generated_items = [] # Expecting a list of Q&A

        except json.JSONDecodeError as e:
            print(f"⚠️ Lỗi phân tích JSON từ Bot API: {e}. Phản hồi: {api_response_str[:300]}...")
            messagebox.showerror("Lỗi Phân Tích", f"Không thể phân tích phản hồi JSON từ Bot API.\nChi tiết: {e}\nPhản hồi (đầu): {api_response_str[:100]}...")
            self.app._last_gen_error_shown = True
            return 0

        existing_question_texts_normalized = {
            q.get("question", "").strip().lower() 
            for q in self.app.all_available_question_objects if q.get("question")
        }
        added_in_this_batch_normalized = set()

        for item in generated_items:
            if isinstance(item, dict) and "question" in item and "answer" in item:
                q_text = str(item["question"]).strip()
                a_text = str(item["answer"]).strip()
                norm_q_text = q_text.lower()

                if not q_text or not a_text:
                    continue
                if norm_q_text in existing_question_texts_normalized or \
                   norm_q_text in added_in_this_batch_normalized:
                    continue

                new_id = self.data_manager.get_next_question_id()
                new_q_obj = {"id": new_id, "question": q_text, "answer": a_text, "source": "api_generated"}
                
                self.app.cau_hoi_data.append(new_q_obj) 
                self.app.all_available_question_objects.append(new_q_obj) 
                
                added_in_this_batch_normalized.add(norm_q_text)
                newly_added_count += 1
        
        if newly_added_count > 0:
            if self.data_manager.save_cau_hoi_data(): # Save to cau_hoi_lien_quan.json
                messagebox.showinfo("Thành Công", f"Đã thêm thành công {newly_added_count} câu hỏi mới từ Bot (API).")
            self.filter_available_questions() # Refresh the listbox
        elif generated_items: # Parsed JSON but no new valid questions
            messagebox.showinfo("Thông Báo", "Bot (API) không tạo được câu hỏi mới hợp lệ (có thể đã tồn tại hoặc rỗng).")
            self.app._last_gen_error_shown = True
        
        return newly_added_count
