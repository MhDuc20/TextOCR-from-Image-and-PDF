import json
import datetime
import random
import string
from bson.objectid import ObjectId # To generate _id similar to MongoDB

# --- Helper Functions (Giữ nguyên) ---
def random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def random_number(min_val, max_val):
    return random.randint(min_val, max_val)

def random_date_iso(start_date, end_date):
    if start_date >= end_date:
        dt = start_date
    else:
        time_difference_seconds = int((end_date - start_date).total_seconds())
        if time_difference_seconds <= 0:
             dt = start_date
        else:
            random_offset_seconds = random.randint(0, time_difference_seconds)
            dt = start_date + datetime.timedelta(seconds=random_offset_seconds)
    return dt.isoformat()

# --- Search Helper Functions ---
def format_vb_summary(vb, include_type=False, vb_type_str=""):
    """Định dạng tóm tắt một văn bản."""
    ngay_bh_str = "N/A"
    if vb.get("ngay_ban_hanh"):
        try:
            ngay_bh_str = datetime.datetime.fromisoformat(vb.get("ngay_ban_hanh")).strftime('%d/%m/%Y')
        except ValueError:
            pass
    type_prefix = f"[{vb_type_str}] " if include_type and vb_type_str else ""
    return f"{type_prefix}Số ký hiệu: {vb.get('so_ky_hieu', 'N/A')}, Trích yếu: '{vb.get('trich_yeu', 'N/A')}', Ngày ban hành: {ngay_bh_str}."

def get_vb_type_str(vb_so_ky_hieu_prefix):
    """Xác định loại văn bản dựa trên tiền tố số ký hiệu (ví dụ)"""
    if vb_so_ky_hieu_prefix.upper().startswith("VBDI"):
        return "Văn bản đi"
    return "Văn bản đến" # Mặc định hoặc nếu không có tiền tố VBDI

def search_vb_by_skh(skh_query, vb_list):
    """Tìm văn bản theo số ký hiệu và trả về thông tin chi tiết."""
    skh_query_lower = skh_query.lower()
    results = [vb for vb in vb_list if skh_query_lower == vb.get("so_ky_hieu", "").lower()]
    if not results:
        return f"Không tìm thấy văn bản nào có số ký hiệu '{skh_query}'."
    
    vb = results[0] # Giả sử số ký hiệu là duy nhất
    vb_type_str = get_vb_type_str(vb.get("so_ky_hieu", ""))
    ngay_bh_str = "N/A"
    if vb.get("ngay_ban_hanh"):
        try:
            ngay_bh_str = datetime.datetime.fromisoformat(vb.get("ngay_ban_hanh")).strftime('%d/%m/%Y')
        except ValueError: pass

    return (f"Thông tin chi tiết [{vb_type_str}] văn bản {skh_query}:\n"
            f"- Số ký hiệu: {vb.get('so_ky_hieu', 'N/A')}\n"
            f"- Trích yếu: {vb.get('trich_yeu', 'N/A')}\n"
            f"- Ngày ban hành: {ngay_bh_str}\n"
            f"- Loại VB ID: {vb.get('id_loai_van_ban', 'N/A')}\n"
            f"- Độ khẩn ID: {vb.get('id_do_khan', 'N/A')}\n"
            f"- Độ mật ID: {vb.get('id_do_mat', 'N/A')}\n"
            f"- Nội dung (tóm tắt): {vb.get('noi_dung', 'N/A')[:150]}{'...' if len(vb.get('noi_dung', '')) > 150 else ''}")

def search_vb_content_by_skh(skh_query, vb_list):
    """Tìm nội dung văn bản theo số ký hiệu."""
    skh_query_lower = skh_query.lower()
    results = [vb for vb in vb_list if skh_query_lower == vb.get("so_ky_hieu", "").lower()]
    if not results:
        return f"Không tìm thấy văn bản nào có số ký hiệu '{skh_query}' để hiển thị nội dung."
    vb_type_str = get_vb_type_str(results[0].get("so_ky_hieu", ""))
    return f"Nội dung của [{vb_type_str}] văn bản {skh_query}:\n{results[0].get('noi_dung', 'N/A')}"

def search_vb_by_keyword(keyword, vb_list, max_results=3):
    """Tìm văn bản theo từ khóa trong trích yếu hoặc nội dung."""
    keyword_lower = keyword.lower()
    results = [
        vb for vb in vb_list
        if keyword_lower in vb.get("trich_yeu", "").lower() or \
           keyword_lower in vb.get("noi_dung", "").lower()
    ]
    if not results:
        return f"Không tìm thấy văn bản nào chứa từ khóa '{keyword}'."
    
    output = f"Tìm thấy {len(results)} văn bản liên quan đến '{keyword}':\n"
    for i, vb in enumerate(results[:max_results]):
        vb_type_str = get_vb_type_str(vb.get("so_ky_hieu", ""))
        output += f"{i+1}. {format_vb_summary(vb, include_type=True, vb_type_str=vb_type_str)}\n"
    if len(results) > max_results:
        output += f"... và {len(results) - max_results} văn bản khác.\n"
    return output.strip()

def search_vb_by_exact_date(date_str_dmY, vb_list, max_results=3):
    """Tìm văn bản theo ngày ban hành chính xác (dd/mm/YYYY)."""
    try:
        target_date_obj = datetime.datetime.strptime(date_str_dmY, "%d/%m/%Y").date()
    except ValueError:
        return f"Định dạng ngày '{date_str_dmY}' không hợp lệ. Vui lòng sử dụng dd/mm/YYYY."

    results = []
    for vb in vb_list:
        if vb.get("ngay_ban_hanh"):
            try:
                vb_date_obj = datetime.datetime.fromisoformat(vb.get("ngay_ban_hanh")).date()
                if vb_date_obj == target_date_obj:
                    results.append(vb)
            except ValueError:
                continue
    if not results:
        return f"Không tìm thấy văn bản nào được ban hành vào ngày {date_str_dmY}."
    
    output = f"Tìm thấy {len(results)} văn bản ban hành ngày {date_str_dmY}:\n"
    for i, vb in enumerate(results[:max_results]):
        vb_type_str = get_vb_type_str(vb.get("so_ky_hieu", ""))
        output += f"{i+1}. {format_vb_summary(vb, include_type=True, vb_type_str=vb_type_str)}\n"
    if len(results) > max_results:
        output += f"... và {len(results) - max_results} văn bản khác.\n"
    return output.strip()

def search_vb_by_month_year(month_year_str, vb_list, max_results=3): # "mm/YYYY"
    """Tìm văn bản theo tháng và năm ban hành."""
    try:
        target_month, target_year = map(int, month_year_str.split('/'))
    except ValueError:
        return f"Định dạng tháng/năm '{month_year_str}' không hợp lệ. Vui lòng sử dụng mm/YYYY."

    results = []
    for vb in vb_list:
        if vb.get("ngay_ban_hanh"):
            try:
                vb_date_obj = datetime.datetime.fromisoformat(vb.get("ngay_ban_hanh"))
                if vb_date_obj.month == target_month and vb_date_obj.year == target_year:
                    results.append(vb)
            except ValueError:
                continue
    if not results:
        return f"Không tìm thấy văn bản nào ban hành trong tháng {month_year_str}."
    
    output = f"Tìm thấy {len(results)} văn bản ban hành trong tháng {month_year_str}:\n"
    for i, vb in enumerate(results[:max_results]):
        vb_type_str = get_vb_type_str(vb.get("so_ky_hieu", ""))
        output += f"{i+1}. {format_vb_summary(vb, include_type=True, vb_type_str=vb_type_str)}\n"
    if len(results) > max_results:
        output += f"... và {len(results) - max_results} văn bản khác.\n"
    return output.strip()

def search_vb_by_year(year_val, vb_list, max_results=3):
    """Tìm văn bản theo năm ban hành."""
    results = []
    for vb in vb_list:
        if vb.get("ngay_ban_hanh"):
            try:
                vb_date_obj = datetime.datetime.fromisoformat(vb.get("ngay_ban_hanh"))
                if vb_date_obj.year == year_val:
                    results.append(vb)
            except ValueError:
                continue
    if not results:
        return f"Không tìm thấy văn bản nào ban hành trong năm {year_val}."
    
    output = f"Tìm thấy {len(results)} văn bản ban hành trong năm {year_val}:\n"
    for i, vb in enumerate(results[:max_results]):
        vb_type_str = get_vb_type_str(vb.get("so_ky_hieu", ""))
        output += f"{i+1}. {format_vb_summary(vb, include_type=True, vb_type_str=vb_type_str)}\n"
    if len(results) > max_results:
        output += f"... và {len(results) - max_results} văn bản khác.\n"
    return output.strip()

def search_newest_vb(vb_list, vb_type_filter=None, max_results=3): # vb_type_filter: "den" or "di"
    """Tìm các văn bản mới nhất, có thể lọc theo loại."""
    temp_list = vb_list
    description = "văn bản"
    if vb_type_filter == "den":
        temp_list = [vb for vb in vb_list if not vb.get("so_ky_hieu", "").upper().startswith("VBDI")]
        description = "văn bản đến"
    elif vb_type_filter == "di":
        temp_list = [vb for vb in vb_list if vb.get("so_ky_hieu", "").upper().startswith("VBDI")]
        description = "văn bản đi"

    if not temp_list:
        return f"Không có {description} nào trong dữ liệu."

    sorted_list = sorted(
        [vb for vb in temp_list if vb.get("ngay_ban_hanh")],
        key=lambda x: datetime.datetime.fromisoformat(x["ngay_ban_hanh"]),
        reverse=True
    )
    if not sorted_list:
        return f"Không có {description} nào có ngày ban hành hợp lệ để sắp xếp."

    output = f"Tìm thấy {len(sorted_list)} {description}, hiển thị {min(len(sorted_list), max_results)} mới nhất:\n"
    for i, vb in enumerate(sorted_list[:max_results]):
        vb_type_str = get_vb_type_str(vb.get("so_ky_hieu", ""))
        output += f"{i+1}. {format_vb_summary(vb, include_type=(not vb_type_filter), vb_type_str=vb_type_str)}\n" # Chỉ hiện type nếu không filter
    return output.strip()

def search_vb_by_do_khan(do_khan_ids, vb_list, vb_type_filter="di", max_results=3):
    """Tìm văn bản theo độ khẩn, mặc định là văn bản đi."""
    temp_list = vb_list
    description = "văn bản"
    if vb_type_filter == "di":
        temp_list = [vb for vb in vb_list if vb.get("so_ky_hieu", "").upper().startswith("VBDI")]
        description = "văn bản đi"
    elif vb_type_filter == "den": # Cho phép tìm cả văn bản đến theo độ khẩn
        temp_list = [vb for vb in vb_list if not vb.get("so_ky_hieu", "").upper().startswith("VBDI")]
        description = "văn bản đến"

    results = [vb for vb in temp_list if vb.get("id_do_khan") in do_khan_ids]
    if not results:
        return f"Không tìm thấy {description} nào có độ khẩn ID trong danh sách {do_khan_ids}."
    
    output = f"Tìm thấy {len(results)} {description} có độ khẩn ID trong {do_khan_ids}:\n"
    for i, vb in enumerate(results[:max_results]):
        vb_type_str = get_vb_type_str(vb.get("so_ky_hieu", ""))
        output += f"{i+1}. {format_vb_summary(vb, include_type=(not vb_type_filter), vb_type_str=vb_type_str)}\n"
    if len(results) > max_results:
        output += f"... và {len(results) - max_results} văn bản khác.\n"
    return output.strip()

def search_vb_by_loai_id(loai_id, vb_list, max_results=3):
    """Tìm văn bản theo ID loại văn bản."""
    results = [vb for vb in vb_list if vb.get("id_loai_van_ban") == loai_id]
    if not results:
        return f"Không tìm thấy văn bản nào thuộc loại ID {loai_id}."
    
    output = f"Tìm thấy {len(results)} văn bản thuộc loại ID {loai_id}:\n"
    for i, vb in enumerate(results[:max_results]):
        vb_type_str = get_vb_type_str(vb.get("so_ky_hieu", ""))
        output += f"{i+1}. {format_vb_summary(vb, include_type=True, vb_type_str=vb_type_str)}\n"
    if len(results) > max_results:
        output += f"... và {len(results) - max_results} văn bản khác.\n"
    return output.strip()

def search_vb_by_do_mat_in_current_quarter(do_mat_id, vb_list, max_results=3):
    """Tìm văn bản theo độ mật trong quý hiện tại."""
    now = datetime.datetime.now()
    current_quarter = (now.month - 1) // 3 + 1
    results = []
    for vb in vb_list:
        if vb.get("ngay_ban_hanh") and vb.get("id_do_mat") == do_mat_id:
            try:
                vb_date = datetime.datetime.fromisoformat(vb.get("ngay_ban_hanh"))
                vb_quarter = (vb_date.month - 1) // 3 + 1
                if vb_date.year == now.year and vb_quarter == current_quarter:
                    results.append(vb)
            except ValueError:
                continue
    if not results:
        return f"Không tìm thấy văn bản nào có độ mật ID {do_mat_id} trong quý này (Quý {current_quarter}/{now.year})."
    
    output = f"Tìm thấy {len(results)} văn bản có độ mật ID {do_mat_id} trong quý này (Quý {current_quarter}/{now.year}):\n"
    for i, vb in enumerate(results[:max_results]):
        vb_type_str = get_vb_type_str(vb.get("so_ky_hieu", ""))
        output += f"{i+1}. {format_vb_summary(vb, include_type=True, vb_type_str=vb_type_str)}\n"
    if len(results) > max_results:
        output += f"... và {len(results) - max_results} văn bản khác.\n"
    return output.strip()

def search_vb_den_by_keyword_year(keyword, year_val, vb_list, max_results=3):
    """Tìm văn bản đến theo từ khóa và năm ban hành."""
    keyword_lower = keyword.lower()
    vb_den_list = [vb for vb in vb_list if not vb.get("so_ky_hieu", "").upper().startswith("VBDI")]
    results = []
    for vb in vb_den_list:
        if vb.get("ngay_ban_hanh") and \
           (keyword_lower in vb.get("trich_yeu", "").lower() or keyword_lower in vb.get("noi_dung", "").lower()):
            try:
                vb_date = datetime.datetime.fromisoformat(vb.get("ngay_ban_hanh"))
                if vb_date.year == year_val:
                    results.append(vb)
            except ValueError:
                continue
    if not results:
        return f"Không tìm thấy văn bản đến nào về '{keyword}' được ban hành trong năm {year_val}."
    
    output = f"Tìm thấy {len(results)} văn bản đến về '{keyword}' ban hành năm {year_val}:\n"
    for i, vb in enumerate(results[:max_results]):
        # Không cần vb_type_str vì đã lọc văn bản đến
        output += f"{i+1}. {format_vb_summary(vb)}\n"
    if len(results) > max_results:
        output += f"... và {len(results) - max_results} văn bản khác.\n"
    return output.strip()


# --- Main Script ---
van_ban_den_filename = "van_ban_den.json"
van_ban_di_filename = "van_ban_di.json"
cau_hoi_filename = "cau_hoi_lien_quan.json"

try:
    print(f"Starting data generation...")
    # 1. Generate data for van_ban_den (Giữ nguyên logic tạo dữ liệu mẫu)
    print(f"\nGenerating 10 records for '{van_ban_den_filename}'...")
    van_ban_den_data = []
    current_year = datetime.datetime.now().year
    start_period_date = datetime.datetime(2023, 1, 1, 0, 0, 0)
    end_period_date = datetime.datetime.now()
    themes = ["hợp tác", "đầu tư", "kế hoạch", "ngân sách", "nhân sự", "báo cáo", "quy định", "chỉ đạo", "thanh tra", "kiểm tra", "dự án Alpha", "công nghệ mới"]
    for i in range(10):
        chosen_theme = random.choice(themes)
        document = {
            "_id": str(ObjectId()),
            "so_ky_hieu": f"VB{random_number(100, 999)}/CV-{random.choice(['UBND', 'BGD', 'BTC'])}",
            "trich_yeu": f"Trích yếu văn bản đến về {chosen_theme} số {i+1} - {random_string(30)}",
            "ngay_ban_hanh": random_date_iso(start_period_date, end_period_date),
            "id_loai_van_ban": random_number(1, 5),
            "id_do_khan": random_number(1, 3),
            "id_do_mat": random_number(1, 3),
            "noi_dung": f"Nội dung chi tiết của văn bản đến liên quan đến {chosen_theme}. {random_string(150)}"
        }
        van_ban_den_data.append(document)
    with open(van_ban_den_filename, 'w', encoding='utf-8') as f:
        json.dump(van_ban_den_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Data for '{van_ban_den_filename}' (10 records) saved to '{van_ban_den_filename}'.")

    # 2. Generate data for van_ban_di (Giữ nguyên logic tạo dữ liệu mẫu)
    print(f"\nGenerating 10 records for '{van_ban_di_filename}'...")
    van_ban_di_data = []
    for i in range(10):
        chosen_theme = random.choice(themes)
        document = {
            "_id": str(ObjectId()),
            "so_ky_hieu": f"VBDI{random_number(1000, 1999)}/CV-{random.choice(['SX', 'KD', 'HC'])}",
            "trich_yeu": f"Trích yếu văn bản đi thảo luận {chosen_theme} lần {i+1} - {random_string(30)}",
            "ngay_ban_hanh": random_date_iso(start_period_date, end_period_date),
            "id_loai_van_ban": random_number(1, 5),
            "id_do_khan": random_number(1, 3),
            "id_do_mat": random_number(1, 3),
            "noi_dung": f"Nội dung văn bản đi về việc {chosen_theme}. {random_string(150)}"
        }
        van_ban_di_data.append(document)
    with open(van_ban_di_filename, 'w', encoding='utf-8') as f:
        json.dump(van_ban_di_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Data for '{van_ban_di_filename}' (10 records) saved to '{van_ban_di_filename}'.")
    print("\n✅ Finished generating văn bản data.")

except Exception as e:
    print(f"❌ An error occurred during văn bản data generation: {e}")
    exit()

# --- Generate cau_hoi_lien_quan.json ---
generated_questions = []
question_id_counter = 1

def add_question(question_text, answer_text):
    global question_id_counter
    generated_questions.append({
        "id": question_id_counter,
        "question": question_text,
        "answer": answer_text
    })
    question_id_counter += 1

try:
    print(f"\nGenerating questions for '{cau_hoi_filename}'...")
    with open(van_ban_den_filename, 'r', encoding='utf-8') as f:
        vb_den_list = json.load(f)
    with open(van_ban_di_filename, 'r', encoding='utf-8') as f:
        vb_di_list = json.load(f)

    all_vb_data = vb_den_list + vb_di_list
    if not all_vb_data:
        print(f"⚠️ Không có dữ liệu từ {van_ban_den_filename} hoặc {van_ban_di_filename} để tạo câu hỏi.")
    else:
        # Lấy dữ liệu mẫu từ all_vb_data (Giữ nguyên logic lấy sample data)
        sample_so_ky_hieu = list(set([vb['so_ky_hieu'] for vb in all_vb_data if 'so_ky_hieu' in vb]))
        sample_trich_yeu_phrases = []
        trich_yeu_contents = [vb['trich_yeu'] for vb in all_vb_data if 'trich_yeu' in vb and vb['trich_yeu']]
        if trich_yeu_contents:
            for _ in range(min(5, len(trich_yeu_contents))):
                full_trich_yeu = random.choice(trich_yeu_contents)
                words = full_trich_yeu.split()
                extracted_phrase = ""
                for theme_word in themes:
                    if theme_word.lower() in full_trich_yeu.lower():
                        try:
                            theme_first_word_lower = theme_word.lower().split()[0]
                            theme_idx = [w.lower() for w in words].index(theme_first_word_lower)
                            phrase_candidate = " ".join(words[theme_idx : min(len(words), theme_idx + random.randint(1,3))])
                            if len(phrase_candidate) > len(theme_word) or len(phrase_candidate.split()) > 1 :
                                extracted_phrase = phrase_candidate
                                break 
                        except ValueError: pass
                if not extracted_phrase and len(words) > 5 :
                    start_search_idx = 0
                    for i, w in enumerate(words):
                        if w.lower() not in ["trích", "yếu", "văn", "bản", "đến", "đi", "về", "thảo", "luận", "số", "lần"] and not w.isnumeric() and len(w) > 2:
                            start_search_idx = i; break
                    if start_search_idx < len(words) -1:
                        phrase_len = random.randint(2, min(4, len(words) - start_search_idx))
                        extracted_phrase = " ".join(words[start_search_idx : start_search_idx + phrase_len])
                if extracted_phrase and len(extracted_phrase) > 5:
                    sample_trich_yeu_phrases.append(extracted_phrase.strip(" .,-"))
        sample_trich_yeu_phrases = list(set(s for s in sample_trich_yeu_phrases if s))
        if not sample_trich_yeu_phrases: 
            sample_trich_yeu_phrases = random.sample(themes, min(3, len(themes))) + ["thông tin chung"]
        sample_dates_str = list(set([datetime.datetime.fromisoformat(vb['ngay_ban_hanh']).strftime('%d/%m/%Y') for vb in all_vb_data if vb.get('ngay_ban_hanh')]))
        sample_years = list(set([datetime.datetime.fromisoformat(vb['ngay_ban_hanh']).year for vb in all_vb_data if vb.get('ngay_ban_hanh')]))
        if not sample_years: sample_years.append(datetime.datetime.now().year)

        # --- Question Templates & Generation with REAL answers ---
        if sample_so_ky_hieu:
            for skh in random.sample(sample_so_ky_hieu, min(2, len(sample_so_ky_hieu))):
                add_question(f"Thông tin chi tiết về văn bản số {skh} là gì?",
                             search_vb_by_skh(skh, all_vb_data))
                add_question(f"Nội dung của văn bản {skh}?",
                             search_vb_content_by_skh(skh, all_vb_data))

        if sample_trich_yeu_phrases:
            for keyword_phrase in random.sample(sample_trich_yeu_phrases, min(3, len(sample_trich_yeu_phrases))):
                add_question(f"Tìm các văn bản liên quan đến '{keyword_phrase}'.",
                             search_vb_by_keyword(keyword_phrase, all_vb_data))
                add_question(f"Có văn bản nào nói về '{keyword_phrase}' không?", # Câu trả lời tương tự
                             search_vb_by_keyword(keyword_phrase, all_vb_data))

        if sample_dates_str:
            for date_str in random.sample(sample_dates_str, min(2, len(sample_dates_str))):
                add_question(f"Liệt kê các văn bản được ban hành vào ngày {date_str}.",
                             search_vb_by_exact_date(date_str, all_vb_data))
        
        current_month_year_str = datetime.datetime.now().strftime("%m/%Y")
        add_question(f"Những văn bản nào được ban hành trong tháng {current_month_year_str}?",
                     search_vb_by_month_year(current_month_year_str, all_vb_data))
        
        if sample_years:
            year_to_query = random.choice(sample_years)
            # Câu hỏi "quan trọng" là chủ quan, ở đây chỉ tìm theo năm
            add_question(f"Các văn bản (quan trọng) nào đã được ban hành trong năm {year_to_query}?",
                         search_vb_by_year(year_to_query, all_vb_data))

        add_question("Tìm các văn bản đến mới nhất.",
                     search_newest_vb(all_vb_data, vb_type_filter="den"))
        add_question("Liệt kê các văn bản đi có độ khẩn cấp cao (ID độ khẩn 2 hoặc 3).",
                     search_vb_by_do_khan([2, 3], all_vb_data, vb_type_filter="di"))
        
        available_loai_vb_ids = list(set(vb.get('id_loai_van_ban') for vb in all_vb_data if vb.get('id_loai_van_ban') is not None))
        if available_loai_vb_ids:
            sample_loai_vb_id = random.choice(available_loai_vb_ids)
            add_question(f"Có văn bản nào thuộc loại ID {sample_loai_vb_id} không?",
                         search_vb_by_loai_id(sample_loai_vb_id, all_vb_data))
        
        available_do_mat_ids = list(set(vb.get('id_do_mat') for vb in all_vb_data if vb.get('id_do_mat') is not None))
        if available_do_mat_ids:
            sample_do_mat_id = random.choice(available_do_mat_ids)
            add_question(f"Tổng hợp các văn bản có độ mật ID {sample_do_mat_id} trong quý này.",
                         search_vb_by_do_mat_in_current_quarter(sample_do_mat_id, all_vb_data))

        if sample_trich_yeu_phrases and sample_years:
            keyword = random.choice(sample_trich_yeu_phrases)
            year = random.choice(sample_years)
            add_question(f"Tìm văn bản đến về '{keyword}' được ban hành năm {year}.",
                         search_vb_den_by_keyword_year(keyword, year, all_vb_data))

        add_question("Văn bản nào được ban hành gần đây nhất?",
                     search_newest_vb(all_vb_data, max_results=1)) # Chỉ 1 văn bản mới nhất
        
        generic_keywords = ["hợp đồng", "quyết định", "thông báo", "công văn", "kế hoạch"]
        for gk in random.sample(generic_keywords, min(2, len(generic_keywords))): # Giảm số lượng để tránh quá nhiều
            add_question(f"Cho tôi xem các văn bản liên quan đến '{gk}'.",
                         search_vb_by_keyword(gk, all_vb_data))

        # Các câu hỏi chung chung vẫn có thể giữ câu trả lời mô tả
        if len(generated_questions) < 20 : # Đảm bảo có đủ câu hỏi gợi ý
            add_question("Làm thế nào để tìm kiếm văn bản theo số ký hiệu?", 
                         "Bạn có thể nhập số ký hiệu đầy đủ của văn bản vào ô tìm kiếm ở Mục 2 (Tìm kiếm nội bộ) hoặc hỏi Chatbot AI ở Mục 3 để được hướng dẫn chi tiết hơn.")
            add_question("Xem các văn bản mới nhất trong tuần này?", 
                         "Để xem văn bản trong tuần này, bạn có thể hỏi Chatbot AI (Mục 3) hoặc sử dụng chức năng tìm kiếm (Mục 2) với các từ khóa ngày tháng cụ thể nếu bạn biết chính xác.")
            add_question("Có thể tìm văn bản theo người ký không?", 
                         "Hiện tại, hệ thống chưa hỗ trợ tìm kiếm trực tiếp theo người ký qua các câu hỏi gợi ý hoặc tìm kiếm nội bộ. Bạn có thể thử hỏi Chatbot AI, có thể nó sẽ hiểu được yêu cầu này nếu thông tin người ký có trong nội dung văn bản.")
            add_question("Thông tin về các dự án đang triển khai?",
                         "Bạn có thể tìm kiếm với từ khóa 'dự án' hoặc tên dự án cụ thể (ví dụ: 'dự án Alpha') trong Mục 2 (Tìm kiếm nội bộ) hoặc hỏi Chatbot AI ở Mục 3 để nhận thông tin liên quan.")

        with open(cau_hoi_filename, 'w', encoding='utf-8') as f:
            json.dump(generated_questions, f, ensure_ascii=False, indent=4)
        print(f"✅ Generated {len(generated_questions)} questions with real data-driven answers and saved to '{cau_hoi_filename}'.")
        print("\n✅ All data generation tasks complete!")

except FileNotFoundError:
    print(f"❌ Error: '{van_ban_den_filename}' or '{van_ban_di_filename}' not found. This shouldn't happen if previous steps ran.")
except Exception as e:
    print(f"❌ An error occurred during question generation: {e}")

