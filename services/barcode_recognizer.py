import numpy as np
import cv2
from pyzbar.pyzbar import decode

def recognize_barcodes(jpeg_bytes, draw_rect=False):
    """
    JPEG 바이트 스트림에서 바코드/QR코드를 인식.
    인식된 바코드 목록을 반환하고, (선택적으로) bounding box 그려진 이미지를 함께 반환.
    """
    img_array = np.frombuffer(jpeg_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        return [], None

    barcodes = decode(img)
    recognized = []

    for barcode in barcodes:
        qr_data = barcode.data.decode("utf-8")
        qr_type = barcode.type
        recognized.append({"type": qr_type, "data": qr_data, "rect": barcode.rect})

        if draw_rect:
            x, y, w, h = barcode.rect
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(img, qr_data, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return recognized, img if draw_rect else None
