import cv2
import pytesseract
from PIL import Image

# Tesseract path (update if yours is different!)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Screen size (adjust for your main screen resolution)
screen_width = 1920
screen_height = 1080

# Load the image using OpenCV
img_cv = cv2.imread(r"C:\Users\ryanw\OneDrive\Desktop\PythonPlateReader\python-ocr.jpg")

# 1. Show Original Image (resized to fit the screen)
img_resized = cv2.resize(img_cv, (screen_width, screen_height))
cv2.imshow("Original Image", img_resized)

# 2. Convert to Grayscale (helps improve OCR)
img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
img_gray_resized = cv2.resize(img_gray, (screen_width, screen_height))
cv2.imshow("Grayscale Image", img_gray_resized)

# 3. Apply Thresholding for better contrast (Binarization)
_, img_thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)
img_thresh_resized = cv2.resize(img_thresh, (screen_width, screen_height))
cv2.imshow("Thresholded Image", img_thresh_resized)

# 4. Resize Image to make text larger (if needed)
img_resized = cv2.resize(img_thresh, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
img_resized = cv2.resize(img_resized, (screen_width, screen_height))
cv2.imshow("Resized Image", img_resized)

# 5. Convert to PIL Image (for Tesseract)
img_pil = Image.fromarray(img_resized)

# 6. Run OCR on the preprocessed image
text = pytesseract.image_to_string(img_pil)

# Print the detected text
print("Detected text:", text)

# Wait for user input to close all windows
cv2.waitKey(0)
cv2.destroyAllWindows()