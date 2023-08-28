import cv2
import numpy as np
import pytesseract
import time

# Set up the path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def improve_image(image):
    # Apply image enhancement techniques here (e.g., unsharp masking, adaptive histogram equalization)
    # Example enhancement applied: unsharp masking
    blurred = cv2.GaussianBlur(image, (0, 0), 10)
    sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)

    return sharpened

def crop_image(image):
    clone = image.copy()
    r = cv2.selectROI(clone)
    cropped_image = clone[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    return cropped_image, (int(r[0]), int(r[1])), (int(r[0] + r[2]), int(r[1] + r[3]))

def blink_rectangle(image, top_left, bottom_right, blink_interval=0.5, num_blinks=5):
    for _ in range(num_blinks):
        image = cv2.rectangle(image, top_left, bottom_right, (0, 255, 255), 2)
        cv2.imshow('Cropped Image', image)
        cv2.waitKey(int(blink_interval * 1000))

        image = cv2.rectangle(image, top_left, bottom_right, (0, 0, 0), 2)
        cv2.imshow('Cropped Image', image)
        cv2.waitKey(int(blink_interval * 1000))

    return image

def add_transparent_rectangle(image, top_left, bottom_right, alpha=0.3):
    overlay = image.copy()
    cv2.rectangle(overlay, top_left, bottom_right, (255, 255, 255), -1)
    image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
    return image

# Open the image file
ImgAdrss="D://BRACU//2023//Summer//CSE471//Project//Backend"
original_image = cv2.imread(ImgAdrss+'//p4.png')

# Improve the original image
improved_image = improve_image(original_image)

# Display the original image
cv2.imshow('Original Image', original_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Display the improved image
cv2.imshow('Improved Image', improved_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Crop the region of interest from the improved image
cropped_image, top_left, bottom_right = crop_image(improved_image)

# Add blinking effect to the rectangle border
cropped_image = blink_rectangle(cropped_image, top_left, bottom_right)

# Add white transparent effect inside the rectangle
cropped_image = add_transparent_rectangle(cropped_image, top_left, bottom_right)

# Display the final result
cv2.imshow('Cropped Image', cropped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Extract text from the cropped region using Tesseract OCR
extracted_text = pytesseract.image_to_string(cropped_image)
print('Extracted Text:', extracted_text)
