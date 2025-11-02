# handlers/ai_chat_handler.py
import tkinter as tk
import threading
import requests
# import re # Không cần regex với cách tiếp cận này

class AIChatHandler:
    def __init__(self, app_instance):
        self.app = app_instance
        # Giả sử bạn đã chuyển sang local transformers, ai_service có thể không còn gemini_model
        # self.ai_service = self.app.ai_service
        # Thay vào đó, bạn có thể cần truy cập trực tiếp qa_pipeline nếu nó được lưu trên app_instance
        # hoặc thông qua một thuộc tính mới trong AIChatHandler nếu _initialize_qa_pipeline được di chuyển vào đây.
        # Dựa trên code trước, ai_service vẫn được dùng để tạo context.
        self.ai_service = self.app.ai_service

        # Các thuộc tính cho local QA (nếu bạn đã tích hợp)
        self.qa_pipeline = None
        self.is_pipeline_ready = False
        HF_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")  # Set token trong .env hoặc system env
        # Kiểm tra và khởi tạo local QA pipeline (nếu có)
        if hasattr(self, '_initialize_qa_pipeline'): # Nếu phương thức này tồn tại
            # Import transformers ở đây để tránh lỗi nếu không cài đặt
            try:
                from transformers import pipeline as hf_pipeline
                self.TRANSFORMERS_AVAILABLE = True
                threading.Thread(target=self._initialize_qa_pipeline, daemon=True).start()
            except ImportError:
                self.TRANSFORMERS_AVAILABLE = False
                print("⚠️ Thư viện transformers chưa được cài đặt. Chức năng QA cục bộ sẽ không hoạt động.")
                print("Vui lòng cài đặt: pip install transformers torch sentencepiece")
        else:
            self.TRANSFORMERS_AVAILABLE = False # Mặc định nếu không có hàm init pipeline

    # Hàm _initialize_qa_pipeline (nếu bạn đã chuyển nó vào đây hoặc đang dùng)
    # Ví dụ:
    # def _initialize_qa_pipeline(self):
    #     # ... logic tải model ...
    #     pass


    def add_to_chat_history(self, message, sender_type="user", is_typing_message=False):
        """Adds a message to the AI chat history display, with bolding for AI responses."""
        if not hasattr(self.app, 'ai_chat_history_text'):
            return
            
        chat_widget = self.app.ai_chat_history_text
        chat_widget.config(state=tk.NORMAL)
        
        current_content = chat_widget.get("1.0", tk.END).strip()
        prefix_for_typing = "" 

        if current_content: 
             chat_widget.insert(tk.END, "\n")

        start_index_for_message = chat_widget.index(tk.END + "-1c") 

        if sender_type == "user":
            chat_widget.insert(tk.END, "Bạn: ", "user_label")
            chat_widget.insert(tk.END, f"{message.strip()}\n", "user_text")
        
        elif sender_type in ["ai", "local_qa", "system_info", "api_chat_bot"]: # Các loại tin nhắn có thể có bold
            if sender_type == "system_info":
                prefix_for_typing = "Hệ thống: "
            elif sender_type == "ai": 
                prefix_for_typing = "AI: "
            elif sender_type == "api_chat_bot":
                prefix_for_typing = "Bot (API): "
            else: # local_qa
                prefix_for_typing = "AI (Local): "

            chat_widget.insert(tk.END, prefix_for_typing, "ai_label")
            
            # Xử lý message để tìm và tô đậm phần trong dấu *
            current_message_text = message.strip()
            last_pos = 0
            while True:
                start_bold = current_message_text.find('*', last_pos)
                if start_bold == -1: # Không còn dấu * mở đầu
                    chat_widget.insert(tk.END, current_message_text[last_pos:], "ai_text")
                    break
            
                end_bold = current_message_text.find('*', start_bold + 1)
                if end_bold == -1: # Không có dấu * đóng, coi phần còn lại là text thường
                    chat_widget.insert(tk.END, current_message_text[last_pos:], "ai_text")
                    break
            
                # Chèn phần text thường trước phần bold
                chat_widget.insert(tk.END, current_message_text[last_pos:start_bold], "ai_text")
                # Chèn phần bold (bỏ dấu *)
                chat_widget.insert(tk.END, current_message_text[start_bold+1:end_bold], ("ai_text", "bold_text"))
            
                last_pos = end_bold + 1
                if last_pos >= len(current_message_text): # Đã xử lý hết chuỗi
                    break
            
            chat_widget.insert(tk.END, "\n\n", "ai_text") # Thêm dòng mới kép sau tin nhắn AI

        else: # Các sender_type khác (nếu có)
            chat_widget.insert(tk.END, f"{message.strip()}\n")
        
        end_index_for_message = chat_widget.index(tk.END + "-1c")

        if is_typing_message: # Logic này áp dụng cho tin nhắn "đang soạn"
            if current_content and chat_widget.get(start_index_for_message + "-1c", start_index_for_message) == '\n':
                 start_idx_for_typing_calc = start_index_for_message
            else: 
                if sender_type == "user":
                    length_to_subtract = len("Bạn: ") + len(message.strip()) + 1 
                else: 
                    typing_prefix = "AI (Local): " 
                    if sender_type == "system_info": typing_prefix = "Hệ thống: "
                    elif sender_type == "ai": typing_prefix = "AI: "
                    elif sender_type == "api_chat_bot": typing_prefix = "Bot (API): "
                    
                    length_to_subtract = len(typing_prefix) + len(message.strip()) + 2 
                start_idx_for_typing_calc = chat_widget.index(f"{end_index_for_message} - {length_to_subtract} chars")
            
            self.app.typing_message_indices = (start_idx_for_typing_calc, end_index_for_message)
        
        chat_widget.see(tk.END)
        chat_widget.config(state=tk.DISABLED)

    def send_to_ai(self):
        """Gửi câu hỏi của người dùng đến AI (local QA hoặc API) và hiển thị câu trả lời."""
        if not hasattr(self.app, 'ai_chat_entry') or not hasattr(self.app, 'ai_chat_history_text'):
            return

        user_query = self.app.ai_chat_entry.get().strip()
        if not user_query: return
        
        self.add_to_chat_history(user_query, "user")
        self.app.ai_chat_entry.delete(0, tk.END)

        # Hiện tại, logic này chỉ hỗ trợ gọi API qua _call_chat_api
        # Nếu bạn muốn tích hợp lại local QA, bạn cần thêm điều kiện kiểm tra
        # self.TRANSFORMERS_AVAILABLE and self.is_pipeline_ready and self.qa_pipeline
        # và gọi _get_local_qa_response_and_update_chat

        # Giả sử bạn có một phương thức _call_chat_api để gọi Bot API
        if hasattr(self, '_call_chat_api') and hasattr(self, '_build_context_for_chat_api'):
            self.add_to_chat_history("Bot (API) đang soạn câu trả lời...", sender_type="api_chat_bot", is_typing_message=True)
            prompt_for_api = self._build_context_for_chat_api(user_query)
            thread = threading.Thread(target=self._get_api_response_and_update_chat, args=(prompt_for_api, user_query))
            thread.daemon = True
            thread.start()
        else:
            self.app.master.after(100, lambda: self.add_to_chat_history("Lỗi: Không có dịch vụ AI nào sẵn sàng (API).", "system_info"))


    def _build_context_for_chat_api(self, user_query):
        """
        Xây dựng ngữ cảnh từ van_ban_den.json và van_ban_di.json dựa trên câu hỏi của người dùng.
        """
        context_parts = ["Dưới đây là một số thông tin liên quan có thể hữu ích từ tài liệu nội bộ:"]
        MAX_CONTEXT_ITEMS = 3 # Số lượng văn bản tối đa đưa vào context
        MAX_CONTENT_SNIPPET_LENGTH = 250 # Độ dài tối đa cho mỗi đoạn trích nội dung
        
        found_items_count = 0
        query_keywords = set(user_query.lower().split()) # Tách từ khóa từ câu hỏi

        # Tìm kiếm trong văn bản đến
        if hasattr(self.app, 'vb_den_data'):
            for vb in self.app.vb_den_data:
                if found_items_count >= MAX_CONTEXT_ITEMS: break
                trich_yeu = vb.get('trich_yeu', '').lower()
                noi_dung = vb.get('noi_dung', '').lower()
                if any(keyword in trich_yeu or keyword in noi_dung for keyword in query_keywords):
                    noi_dung_snippet = vb.get('noi_dung', '')[:MAX_CONTENT_SNIPPET_LENGTH]
                    if len(vb.get('noi_dung', '')) > MAX_CONTENT_SNIPPET_LENGTH:
                        noi_dung_snippet += "..."
                    context_parts.append(
                        f"\n--- VĂN BẢN ĐẾN ---\n"
                        f"Số ký hiệu: {vb.get('so_ky_hieu', 'N/A')}\n"
                        f"Trích yếu: {vb.get('trich_yeu', 'N/A')}\n"
                        f"Nội dung tóm tắt: {noi_dung_snippet}"
                    )
                    found_items_count += 1

        # Tìm kiếm trong văn bản đi
        if hasattr(self.app, 'vb_di_data'):
            for vb in self.app.vb_di_data:
                if found_items_count >= MAX_CONTEXT_ITEMS: break
                trich_yeu = vb.get('trich_yeu', '').lower()
                noi_dung = vb.get('noi_dung', '').lower()
                if any(keyword in trich_yeu or keyword in noi_dung for keyword in query_keywords):
                    noi_dung_snippet = vb.get('noi_dung', '')[:MAX_CONTENT_SNIPPET_LENGTH]
                    if len(vb.get('noi_dung', '')) > MAX_CONTENT_SNIPPET_LENGTH:
                        noi_dung_snippet += "..."
                    context_parts.append(
                        f"\n--- VĂN BẢN ĐI ---\n"
                        f"Số ký hiệu: {vb.get('so_ky_hieu', 'N/A')}\n"
                        f"Trích yếu: {vb.get('trich_yeu', 'N/A')}\n"
                        f"Nội dung tóm tắt: {noi_dung_snippet}"
                    )
                    found_items_count += 1

        if found_items_count > 0:
            context_str = "\n".join(context_parts)
            # Giới hạn độ dài tổng thể của context để tránh prompt quá dài
            MAX_TOTAL_CONTEXT_LENGTH = 3000 
            if len(context_str) > MAX_TOTAL_CONTEXT_LENGTH:
                context_str = context_str[:MAX_TOTAL_CONTEXT_LENGTH] + "\n... (ngữ cảnh đã được rút gọn)"
            
            # Ghép ngữ cảnh với câu hỏi của người dùng
            final_prompt = f"{context_str}\n\n--- CÂU HỎI CỦA NGƯỜI DÙNG ---\n{user_query}\n\n--- TRẢ LỜI (dựa trên ngữ cảnh nếu có và kiến thức của bạn) ---\n"
            return final_prompt
        else:
            # Nếu không tìm thấy ngữ cảnh, chỉ gửi câu hỏi
            return f"--- CÂU HỎI CỦA NGƯỜI DÙNG ---\n{user_query}\n\n--- TRẢ LỜI (dựa trên kiến thức của bạn) ---\n"

    def _get_api_response_and_update_chat(self, prompt_or_query, original_user_query):
        """Lấy phản hồi từ Bot API (chạy trong thread)."""
        api_response_text = ""
        try:
            # Gọi phương thức _call_chat_api đã được định nghĩa
            api_response_text = self._call_chat_api(prompt_or_query)
            if api_response_text.startswith("Lỗi:"): # Nếu _call_chat_api trả về lỗi dạng chuỗi
                 raise Exception(api_response_text)
        except Exception as e: 
            print(f"❌ Lỗi khi gọi API Chat Bot: {e}")
            api_response_text = f"Xin lỗi, đã có lỗi xảy ra khi kết nối với Bot API: {e}"
        self.app.master.after(0, self._update_chat_after_ai_response, api_response_text, original_user_query, "api_chat_bot")

    # Phương thức này cần được định nghĩa để gọi Bot API của bạn
    # Nó được gọi từ available_questions_handler và send_to_ai
    def _call_chat_api(self, user_input_prompt):
        """
        Gửi yêu cầu đến Chat API và trả về phản hồi dưới dạng text.
        Đây là một ví dụ, bạn cần điều chỉnh cho phù hợp với API của mình.
        """
        # Lấy URL và model từ UI (nếu có) hoặc dùng giá trị mặc định
        api_url = "http://192.168.0.118:5000/chat" # URL API Chat của bạn
        selected_model = "default_chat_model" # Model mặc định hoặc lấy từ combobox

        if hasattr(self.app, 'ai_model_select_combobox'):
            current_model_on_ui = self.app.ai_model_select_combobox.get()
            if current_model_on_ui:
                selected_model = current_model_on_ui
        
        print(f"Gọi Chat API: {api_url} với model: {selected_model}")
        payload = {
            "model": selected_model,
            "prompt": user_input_prompt,
            "stream": False # Giả sử API không stream cho trường hợp này
        }
        try:
            response = requests.post(api_url, json=payload, timeout=180) # Tăng timeout
            response.raise_for_status()
            response_json = response.json()
            
            # Kiểm tra cấu trúc JSON trả về từ API của bạn
            # Ví dụ: nếu API trả về {"message": {"content": "phản hồi"}}
            if "message" in response_json and "content" in response_json["message"]:
                return response_json["message"]["content"]
            # Ví dụ: nếu API trả về {"choices": [{"message": {"content": "phản hồi"}}]}
            elif "choices" in response_json and response_json["choices"] and \
                 "message" in response_json["choices"][0] and \
                 "content" in response_json["choices"][0]["message"]:
                return response_json["choices"][0]["message"]["content"]
            # Ví dụ: nếu API trả về trực tiếp một chuỗi trong một key nào đó
            elif "response" in response_json: # Hoặc "text", "answer", etc.
                return response_json["response"]
            else:
                # Nếu không khớp, cố gắng chuyển toàn bộ JSON thành string để debug
                print(f"⚠️ API Chat trả về cấu trúc JSON không mong muốn: {response_json}")
                return f"Lỗi: API trả về cấu trúc không mong muốn. {str(response_json)[:200]}..."

        except requests.exceptions.Timeout:
            print("❌ Lỗi: Hết thời gian chờ khi gọi Chat API.")
            return "Lỗi: Hết thời gian chờ khi kết nối với Bot API."
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try: error_detail = e.response.json()
                except ValueError: error_detail = e.response.text
            print(f"❌ Lỗi Chat API: {error_detail}")
            return f"Lỗi: Không thể kết nối hoặc xử lý yêu cầu với Bot API. ({error_detail})"
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi gọi Chat API: {e}")
            return f"Lỗi: Đã có lỗi không mong muốn xảy ra. ({e})"

    def _update_chat_after_ai_response(self, response_text, original_user_query, sender_type_for_response="ai"):
        """Cập nhật chat UI sau khi có phản hồi AI (Local QA hoặc API)."""
        if hasattr(self.app, 'typing_message_indices') and self.app.typing_message_indices:
            if hasattr(self.app, 'ai_chat_history_text'):
                chat_widget = self.app.ai_chat_history_text
                chat_widget.config(state=tk.NORMAL)
                try:
                    start_idx_str, end_idx_str = self.app.typing_message_indices
                    if chat_widget.compare(start_idx_str, "<=", tk.END + "-1c") and \
                       chat_widget.compare(end_idx_str, "<=", tk.END + "-1c") and \
                       (chat_widget.compare(start_idx_str, "<", end_idx_str) or \
                        chat_widget.compare(start_idx_str, "==", end_idx_str)):
                        chat_widget.delete(start_idx_str, end_idx_str)
                    else:
                        print(f"Cảnh báo: Chỉ số không hợp lệ để xóa tin nhắn đang soạn: {self.app.typing_message_indices}")
                except tk.TclError as e_del:
                    print(f"Lỗi TclError khi xóa tin nhắn đang soạn: {e_del}. Indices: {self.app.typing_message_indices}")
                except Exception as e_gen:
                    print(f"Lỗi không xác định khi xóa tin nhắn đang soạn: {e_gen}. Indices: {self.app.typing_message_indices}")
                self.app.typing_message_indices = None
                chat_widget.config(state=tk.DISABLED)
        self.add_to_chat_history(response_text, sender_type_for_response)

    # Các thuộc tính và phương thức liên quan đến chọn model API
    # (Nếu bạn muốn quản lý danh sách model và lựa chọn trong handler này)
    AVAILABLE_AI_MODELS = ["qwen2.5vl:7b","llama3.2-vision","deepseek-r1:8b", "deepseek-r1:32b", "llava:13b-v1.6", "mistral:7b-instruct-v0.3-q6_K"] # Ví dụ
    selected_ai_model = AVAILABLE_AI_MODELS[0] # Mặc định

    def set_selected_model(self, model_name):
        if model_name in self.AVAILABLE_AI_MODELS:
            self.selected_ai_model = model_name
            print(f"ℹ️ Model AI được chọn: {self.selected_ai_model}")
            # Có thể thêm logic thông báo cho người dùng trong chat nếu cần
            # self.add_to_chat_history(f"Đã chuyển sang model: {model_name}", "system_info")
        else:
            print(f"⚠️ Model không hợp lệ được chọn: {model_name}")