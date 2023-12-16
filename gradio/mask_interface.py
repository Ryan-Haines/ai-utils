import gradio as gr
import PIL.Image
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

def is_valid_image(file):
    try:
        img = PIL.Image.open(io.BytesIO(file.read()))
        file.seek(0)  # Reset file pointer for future reads
        return True
    except:
        return False
    
def create_blank_image_with_text(text):
    image = Image.new('RGB', (300, 300), color = (73, 109, 137))
    d = ImageDraw.Draw(image)
    fnt = ImageFont.load_default()
    d.text((10,10), text, font=fnt, fill=(255, 255, 0))
    return image

def process_images(images):
    thumbnails = []
    for img in images:
        if is_valid_image(img):
            thumbnails.append(ImageOps.exif_transpose(PIL.Image.open(io.BytesIO(img.read()))))
        else:
            img.seek(0)  # Reset file pointer if not an image

    if not thumbnails:
        return create_blank_image_with_text("No valid images found")
    return thumbnails

iface = gr.Interface(
    process_images, 
    [gr.inputs.File(type="file", label="Drag & Drop")], 
    gr.outputs.Image(type="pil", label="Thumbnails"),
    live=True,
    server_name="0.0.0.0",
    server_port=8080,
    analytics_enabled=False
)

iface.launch()
