import requests
import cv2
import numpy as np
from PIL import Image
import pytesseract
from io import BytesIO
import urllib3
import os
import base64
from bs4 import BeautifulSoup

# 轉換 Base64 為原始字串
def from_base64(b64_text):
    return base64.b64decode(b64_text).decode()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image):
    """ 使用 OpenCV 進行影像前處理，提高 OCR 辨識率 """
    image = np.array(image)  # 轉成 OpenCV 格式
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 轉為灰階
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # 降噪
    _, binary = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # 二值化
    return Image.fromarray(binary)  # 轉回 PIL 格式

# 建立 session
session = requests.Session()
session.get("https://ecare.nfu.edu.tw/login/authout?out=1", verify=False)

def download_and_parse_captcha(session, url, save_path):
    response = session.get(url, verify=False)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image = preprocess_image(image)  # 影像前處理
        
        # 儲存處理後的圖片
        image.save(save_path)
        
        # OCR 辨識
        text = pytesseract.image_to_string(image, config='--psm 7 --oem 3')
        return text.strip()
    else:
        raise Exception("Failed to download captcha")

captcha_url = "https://ecare.nfu.edu.tw/ext/authimg?rnd=0.30101149229578916"
save_directory = "captchas"
os.makedirs(save_directory, exist_ok=True)  # 確保資料夾存在
save_path = os.path.join(save_directory, "processed_captcha.png")
soup = None
while soup is None:
    parsed_text = download_and_parse_captcha(session, captcha_url, save_path)
    print("圖片已儲存至:", save_path)
    print("解析出的文字:", parsed_text)
    data = {
        "login_acc": "username_base64",
        "login_pwd": "password_base64",
    }
    # 將字典內的每個值解碼回原始字串
    data = {key: base64.b64decode(value).decode("utf-8") for key, value in data.items()}
    data["login_chksum"] = parsed_text
    url = "https://ecare.nfu.edu.tw/login/auth"
    response = session.post(url, data=data, verify=False)

    print("response:", response)
    print("Response data:")
    print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find(class_="bt_logout")
    
for key, value in response.headers.items():
    print(f"{key}: {value}")
print("解析出的文字:", parsed_text)
print("圖片已儲存至:", save_path)

import json
import urllib3
url = "https://ecare.nfu.edu.tw/mentorajax/allstdnoauto"
print("REQ HEADERS")
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://ecare.nfu.edu.tw/desktop/officeleave?act=add",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
})
for i in range(1, 61):
    data = {
        "std": f"412481{i:02d}"
    }
    # 41043257
    # 41043108
    response = session.post(url, data=data, verify=False)
    response_data=[]
    try:
        response_data = response.json()
    except json.decoder.JSONDecodeError:
        print(f"Student ID: {data['std']} is invalid")
    print(response_data)
    if len(response_data) > 0:
        continue
    # Print the data in a readable format
    for student in response_data:
        print("-" * 30)
        print(f"Student Number: {student['STUD_NO']}")
        print(f"Name: {student['STUD_CNAME']}")
        print(f"Sex: {'Male' if student['STUD_SEX'] == '1' else 'Female'}")
        print(f"Class Number: {student['CLSS_NO']}")
        print(f"Color Number: {student['STUD_COLO_NO']}")
        print(f"Class Name: {student['CLSS_SNAME']}")
        print("-" * 30)

session.get("https://ecare.nfu.edu.tw/login/authout?out=1", verify=False)