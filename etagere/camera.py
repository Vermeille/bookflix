from pyzbar.pyzbar import decode
from PIL import Image


def scan_barcode(image_path):
    img = Image.open(image_path).convert("RGB")
    barcodes = decode(img)
    print(barcodes)
    if barcodes:
        return barcodes[0].data.decode("utf-8")
    return None
