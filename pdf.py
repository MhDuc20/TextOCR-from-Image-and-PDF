import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os # Thêm os để kiểm tra file

# --- Tesseract Configuration ---
TESSERACT_CMD_PATH = None
TESSDATA_PREFIX_PATH = None

def configure_tesseract(tesseract_cmd=None, tessdata_prefix=None):
    """Cấu hình đường dẫn Tesseract và TESSDATA_PREFIX."""
    global TESSERACT_CMD_PATH, TESSDATA_PREFIX_PATH
    if tesseract_cmd:
        TESSERACT_CMD_PATH = tesseract_cmd
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH
    if tessdata_prefix:
        TESSDATA_PREFIX_PATH = tessdata_prefix
        os.environ["TESSDATA_PREFIX"] = TESSDATA_PREFIX_PATH

def extract_text_from_image_page(page_object, language='vie'):
    """
    Trích xuất văn bản từ một đối tượng fitz.Page sử dụng OCR.
    page_object: Một đối tượng fitz.Page.
    language: Ngôn ngữ cho OCR (ví dụ: 'vie' cho tiếng Việt).
    Trả về văn bản đã trích xuất hoặc một chuỗi thông báo lỗi.
    """
    try:
        # Đảm bảo Tesseract được cấu hình nếu TESSERACT_CMD_PATH được đặt
        if TESSERACT_CMD_PATH and pytesseract.pytesseract.tesseract_cmd != TESSERACT_CMD_PATH:
             pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH
        
        # Kiểm tra TESSDATA_PREFIX nếu được đặt toàn cục
        if TESSDATA_PREFIX_PATH and os.environ.get("TESSDATA_PREFIX") != TESSDATA_PREFIX_PATH:
            os.environ["TESSDATA_PREFIX"] = TESSDATA_PREFIX_PATH

        pix = page_object.get_pixmap(alpha=False) # alpha=False để có RGB
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img, lang=language)
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        return "Lỗi: Tesseract OCR không được cài đặt hoặc không tìm thấy trong PATH."
    except pytesseract.TesseractError as e: # Bắt lỗi cụ thể của Tesseract (ví dụ: thiếu file ngôn ngữ)
        return f"Lỗi Tesseract OCR: {e}"
    except Exception as e:
        return f"Lỗi không xác định khi OCR: {e}"

if __name__ == "__main__":
    # Cấu hình Tesseract mặc định cho kiểm thử (nếu có)
    default_windows_tess_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    default_windows_tessdata = r'C:\Program Files\Tesseract-OCR\tessdata'
    if os.path.exists(default_windows_tess_path) and os.path.isdir(default_windows_tessdata):
        configure_tesseract(tesseract_cmd=default_windows_tess_path, tessdata_prefix=default_windows_tessdata)
        print(f"Đã tự động cấu hình Tesseract cho kiểm thử: {default_windows_tess_path}")
    else:
        print("Lưu ý: Không tìm thấy Tesseract tại đường dẫn mặc định cho kiểm thử. Cấu hình thủ công nếu cần.")

    pdf_file_path_test = "input.pdf" # Thay thế bằng file PDF kiểm thử của bạn
    if not os.path.exists(pdf_file_path_test):
        print(f"Lỗi: Không tìm thấy file '{pdf_file_path_test}' để kiểm thử.")
    else:
        try:
            doc = fitz.open(pdf_file_path_test)
            if len(doc) > 0:
                print(f"\n--- Trích xuất trang 1 của '{pdf_file_path_test}' ---")
                page_to_ocr = doc.load_page(0) # OCR trang đầu tiên
                extracted_text = extract_text_from_image_page(page_to_ocr, language='vie')
                print("Văn bản trích xuất:")
                print(extracted_text)
            else:
                print(f"File '{pdf_file_path_test}' không có trang nào.")
            doc.close()
        except Exception as e:
            print(f"Lỗi khi mở hoặc xử lý PDF kiểm thử: {e}")