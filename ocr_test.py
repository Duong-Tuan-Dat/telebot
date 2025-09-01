import pytesseract
from PIL import Image

# Chỉ đường dẫn đến file exe (nếu chưa add PATH)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Mở ảnh
img = Image.open("Screenshot 2025-08-30 163443.png")

# Chạy OCR
text = pytesseract.image_to_string(img, lang="vie")
print(text)
