from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Load BLIP for image captioning
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def describe_image(image_path):
    """Generate a text caption from an image."""
    img = Image.open(image_path).convert("RGB")
    inputs = processor(img, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=30)
    return processor.decode(out[0], skip_special_tokens=True)
