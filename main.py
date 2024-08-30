import glob
import os
import cv2
from emailing import send_email
import streamlit as st
from datetime import datetime

st.title("Motion Detector")
start = st.button("Start camera")

if start:
    streamlit_image = st.image([])
    video = cv2.VideoCapture(0)

    first_frame = None
    status_list = []
    count = 1

    def clean_folder():
        images = glob.glob("images/*png")
        for image in images:
            os.remove(image)

    while True:
        status = 0
        now = datetime.now()
        check, frame = video.read()

        # turn it to gray scale and blury
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

        # set the first frame to compare to
        if first_frame is None:
            first_frame = gray_frame_gau

        # compare first frame to new frame
        delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

        # if colour +30 assign to 255 (make less fuzzy)
        # Thresh_binary = algorithm
        thresh_frame = cv2.threshold(delta_frame, 65, 255, cv2.THRESH_BINARY)[1]

        # remove noise (dilate)
        dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

        # contours (anything small will not be counted?)
        contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 20000:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (91, 14, 235), 3)
            # FRAME? top corner, bottom corner, line color, line width

            if rectangle.any():
                status = 1

                # if rectangle, save images in folder
                cv2.imwrite(f"images/{count}.png", frame)
                count = count + 1
                all_images = glob.glob("images/*.png")
                index = int(len(all_images) / 2)
                image_with_object = all_images[index]

        status_list.append(status)
        status_list = status_list[-2:]

        if status_list[0] == 1 and status_list[1] == 0:
            send_email(image_with_object)
            clean_folder()

        cv2.putText(img=frame, text=now.strftime("%A"), org=(30, 80),
                    fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3,
                    color=(245, 10, 139), thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(img=frame, text=now.strftime("%H:%M:%S"), org=(30, 140),
                    fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3,
                    color=(245, 143, 10), thickness=2, lineType=cv2.LINE_AA)

        streamlit_image.image(frame)

        key = cv2.waitKey(1)

        # stop the loop when you press Q
        if key == ord("q"):
            break

    video.release()
