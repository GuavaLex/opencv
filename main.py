import glob
import os
from threading import Thread
import cv2
import time
from email_part import send_email


first_frame = None
video = cv2.VideoCapture(0)
time.sleep(1)
status_list = []
count = 1

def clean_folder():
    images = glob.glob("images/*.png")
    for i in images:
        os.remove(i)
while True:
    status = 0
    check, frame = video.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_blur = cv2.GaussianBlur(gray_frame,(21,21),0)
    cv2.imshow("My video", gray_frame_blur)

    if first_frame is None:
        first_frame = gray_frame_blur

    delta_frame = cv2.absdiff(first_frame, gray_frame_blur)
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
    cv2.imshow("My Video", dil_frame)

    contours, check = cv2.findContours(dil_frame,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

        if rectangle.any():
            status = 1
            cv2.imwrite(f"images/{count}.png", frame)
            count = count + 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images)/2)
            images_with_objects = all_images[index]



    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[0] == 1 and status_list[1] == 1:
        email_thread = Thread(target=send_email, args=images_with_objects)
        email_thread.daemon = True
        clean_thread = Thread(target=clean_thread)
        clean_thread.daemon = True

        email_thread.start()



    cv2.imshow("Video", frame)
    key = cv2.waitKey(1)

    if key == ord("q"):
        break

video.release()

clean_thread.start()