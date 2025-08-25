import cv2
import pytesseract
import numpy as np
cascade = cv2.CascadeClassifier("haarcascade_russian_plate_number.xml")
states = {
    "AN": "Andaman and Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CH": "Chandigarh",
    "CT": "Chhattisgarh",
    "DN": "Dadra and Nagar Haveli and Daman and Diu",
    "DL": "Delhi",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JK": "Jammu and Kashmir",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LD": "Lakshadweep",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "PY": "Puducherry",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "WB": "West Bengal"
}

registered_plates=["TN0143034","TN22at9066"]
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'


def extract_num(img_name):
    global read
    img = cv2.imread(img_name)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    nplate = cascade.detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in nplate:
        a, b = (int(0.02*img.shape[0]), int(0.025*img.shape[1]))
        plate = img[y+a:y+h-a, x+b:x+w-b, :]

        kernel = np.ones((1, 1), np.uint8)
        plate = cv2.dilate(plate, kernel, iterations=1)
        plate = cv2.erode(plate, kernel, iterations=1)
        plate_gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
        (thresh, plate) = cv2.threshold(plate_gray, 127, 255, cv2.THRESH_BINARY)

        read = pytesseract.image_to_string(plate)
        print(read)
        read = ''.join(e for e in read if e.isalnum())
        state = read[0:2]
        print(read)
        if state in states:
            try:
                print('Car belongs to', states[state])
            except:
                print('state not recognised!!')
            print("Registration number : ",read[0:2],read[2:4],read[4:6].upper(),read[6:])
            print("Available in the database")
            cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 2)
            cv2.rectangle(img, (x, y-40), (x+w, y), (0,255,0), -1)
            cv2.putText(img, read, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (255,255,255), thickness=4)

            cv2.imwrite('result.jpg', img)
            cv2.imshow('Plate', plate)
            cv2.imshow("Result", img)   
        else:
            print("Registration number : ",read[0:2],read[2:4],read[4:6].upper(),read[6:])
            print("Fake register Number")
            cv2.rectangle(img, (x, y), (x+w, y+h), (0,0,255), 2)
            cv2.rectangle(img, (x, y-40), (x+w, y), (0,0,255), -1)
            cv2.putText(img, "FAKE", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (255, 255, 255), thickness=4)

            cv2.imshow('Plate', plate)
            cv2.imshow("Result", img)
            cv2.imwrite('result.jpg', img)
        cv2.waitKey(300)
        cv2.destroyAllWindows() 


extract_num(r"D:\\REKHA PROJECT\\CAR 5.jpg")