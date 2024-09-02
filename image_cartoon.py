from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

app = FastAPI()

def cartoonize_image(image_bytes: BytesIO) -> BytesIO:
    # Read the image from bytes
    file_bytes = np.asarray(bytearray(image_bytes.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Resize image for better performance
    img = cv2.resize(img, (800, 600))

    # Apply bilateral filter to smoothen the image while preserving edges
    bilateral_filter = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)

    # Convert image to grayscale
    gray = cv2.cvtColor(bilateral_filter, cv2.COLOR_BGR2GRAY)

    # Apply median blur to the grayscale image
    gray = cv2.medianBlur(gray, 7)

    # Apply adaptive thresholding to create an edge mask
    edges = cv2.adaptiveThreshold(gray, 255,
                                 cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY,
                                 9, 10)

    # Apply bilateral filter again to smoothen the colors
    color = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)

    # Combine the edge mask with the smoothed image
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    # Convert result to BytesIO
    _, buffer = cv2.imencode('.png', cartoon)
    img_byte_arr = BytesIO(buffer)
    img_byte_arr.seek(0)
    
    return img_byte_arr

@app.post("/cartoonize/")
async def cartoonize(file: UploadFile = File(...)):
    # Read the uploaded file
    image_bytes = await file.read()
    image_stream = BytesIO(image_bytes)
    
    # Cartoonize the image
    cartoon_img = cartoonize_image(image_stream)

    # Return the image as a streaming response
    return StreamingResponse(cartoon_img, media_type="image/png")
