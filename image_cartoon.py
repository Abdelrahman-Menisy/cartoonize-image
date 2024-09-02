from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from rembg import remove
from io import BytesIO
from PIL import Image

app = FastAPI()

@app.post("/remove-background/")
async def remove_background(file: UploadFile = File(...)):
    # Read the uploaded file
    image = Image.open(file.file)

    # Convert image to bytes
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')

    # Remove the background
    output = remove(img_byte_arr.getvalue())

    # Convert back to an image
    img_result = Image.open(BytesIO(output))

    # Save the result to a BytesIO object
    img_byte_arr = BytesIO()
    img_result.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Return the image directly as the response without a download link
    return StreamingResponse(img_byte_arr, media_type="image/png")
