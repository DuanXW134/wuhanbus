import easyocr
import yolov5
import cv2
import numpy as np
from PIL import Image


def myOCR(path) :
    print("ocr begin")
    model = yolov5.load("./best.pt")
    image = Image.open(path)

    # 转换为NumPy数组
    image_array = np.array(image)

    predictions = model(image_array)
    print("/////////////////////////////")
    print(predictions.xyxy[0].numpy())
    boxes = predictions.xyxy[0].numpy()
    for box in boxes:
       x1, y1, x2, y2 , confidence, classNumber = box
       cropped_image = image_array[int(y1):int(y2), int(x1):int(x2)]
    
       # 处理裁剪后的图像，例如保存到文件
       cv2.imwrite('./out/out.jpg', cropped_image)

    reader = easyocr.Reader(["en"])

    # 指定要识别的图像文件路径
    image_path = "./out/out.jpg"

    # 使用EasyOCR库识别图像中的文本
    result = reader.readtext(image_path)

    # 打印识别结果
    for r in result:
        print(r[1])
        return r[1]
    # return result[0][1]

# myOCR("./bus4.jpg")
