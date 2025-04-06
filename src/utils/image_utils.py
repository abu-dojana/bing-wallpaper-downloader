def resize_image(image, size):
    from PIL import Image
    return image.resize(size, Image.ANTIALIAS)

def save_image(image, path):
    image.save(path)

def load_image(path):
    from PIL import Image
    return Image.open(path)

def convert_image_format(image, format):
    from io import BytesIO
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=format)
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()