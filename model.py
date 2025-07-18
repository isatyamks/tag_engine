import cv2
from ultralytics import YOLO
from PIL import Image
import os
import numpy as np
from datetime import datetime

from src.similar import similar

model = YOLO("weights\\epoch_3\\best.pt")

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = f"video_crops\\crops_{timestamp}"
video_path = "data\\instagram_reels\\2025-05-31_14-01-37_UTC.mp4"

def main():
    names = model.names
    conf_threshold = 0.6
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    frame_skip = 5 
    frame_count = 0
    saved_crops = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip != 0:
            frame_count += 1
            continue

        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        results = model(frame)[0]

        for i, (box, conf, cls) in enumerate(zip(results.boxes.xyxy, results.boxes.conf, results.boxes.cls)):
            if conf < conf_threshold:
                continue

            x1, y1, x2, y2 = map(int, box)
            cropped = pil_image.crop((x1, y1, x2, y2))
            class_id = int(cls.item())
            class_name = names[class_id]

            is_dup = False
            for saved in saved_crops:
                if similar(cropped, saved):
                    is_dup = True
                    break
            if is_dup:
                continue

            saved_crops.append(cropped)
            crop_filename = f"{output_dir}/{class_name}__{conf:.2f}.jpg"
            cropped.save(crop_filename)
            print(f"Saved unique: {crop_filename}")

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
