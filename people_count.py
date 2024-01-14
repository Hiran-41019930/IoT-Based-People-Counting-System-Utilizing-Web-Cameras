import os
import cv2
import pandas as pd
from datetime import datetime, timedelta

# Initialize variables
person_id_counter1 = 1
person_id_counter2 = 1
person_ids1 = set()
person_ids2 = set()
trackers1 = {}
trackers2 = {}

# Set the path to the Haar cascade XML file for upper body detection
cascade_path = "C:/Users/hiran/Desktop/haarcascade_upperbody.xml"

# Load the pre-trained Haar cascade for upper body detection
cascade = cv2.CascadeClassifier(cascade_path)

# Set up video captures for two web cameras
cap1 = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use index 0 for the first webcam
cap2 = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # Use index 1 for the second webcam

# Check if the video captures are successfully opened
if not cap1.isOpened() or not cap2.isOpened():
    print("Failed to open one of the webcams")
    exit()

# Create separate windows for each camera
cv2.namedWindow("Camera 1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera 2", cv2.WINDOW_NORMAL)

# Initialize variables for Excel logging
excel_data1 = {"Timestamp": [], "Detections": []}
excel_data2 = {"Timestamp": [], "Detections": []}
start_time = datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)  # Initialize to midnight

# Create a folder named "Total-Detection" on the desktop if it doesn't exist
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
folder_path = os.path.join(desktop_path, "Total-Detection")
os.makedirs(folder_path, exist_ok=True)

# Load the previous day's data if available
previous_day_file1 = os.path.join(folder_path, (start_time - timedelta(days=1)).strftime("%A") + "-camera1-detections.xlsx")
previous_day_file2 = os.path.join(folder_path, (start_time - timedelta(days=1)).strftime("%A") + "-camera2-detections.xlsx")

if os.path.exists(previous_day_file1):
    previous_day_data1 = pd.read_excel(previous_day_file1)
    excel_data1.update(previous_day_data1.iloc[-1].to_dict())

if os.path.exists(previous_day_file2):
    previous_day_data2 = pd.read_excel(previous_day_file2)
    excel_data2.update(previous_day_data2.iloc[-1].to_dict())

# Initialize Excel file paths
day_name = start_time.strftime("%A")
excel_file_path1 = os.path.join(folder_path, f"{day_name}-camera1-detections.xlsx")
excel_file_path2 = os.path.join(folder_path, f"{day_name}-camera2-detections.xlsx")

# Write initial header to Excel files
if not os.path.exists(excel_file_path1):
    pd.DataFrame(columns=excel_data1.keys()).to_excel(excel_file_path1, index=False)

if not os.path.exists(excel_file_path2):
    pd.DataFrame(columns=excel_data2.keys()).to_excel(excel_file_path2, index=False)

while True:
    # Read a frame from the first webcam
    ret1, frame1 = cap1.read()

    # Read a frame from the second webcam
    ret2, frame2 = cap2.read()

    # Check if the frames were successfully read
    if not ret1 or not ret2:
        break

    # Convert the frames to grayscale
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Perform upper body detection using the Haar cascade for the first webcam
    upper_bodies1 = cascade.detectMultiScale(gray1, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    # Perform upper body detection using the Haar cascade for the second webcam
    upper_bodies2 = cascade.detectMultiScale(gray2, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    # Update existing trackers and check for new persons for the first webcam
    for person_id, tracker in trackers1.items():
        success, bbox = tracker.update(frame1)
        if success:
            (x, y, w, h) = [int(v) for v in bbox]
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Add a green box around the tracked person
            person_ids1.add(person_id)

    # Update existing trackers and check for new persons for the second webcam
    for person_id, tracker in trackers2.items():
        success, bbox = tracker.update(frame2)
        if success:
            (x, y, w, h) = [int(v) for v in bbox]
            cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Add a green box around the tracked person
            person_ids2.add(person_id)

    # Iterate over detected upper bodies for the first webcam
    for (x, y, w, h) in upper_bodies1:
        # Create a new tracker for each detected person
        bbox = (x, y, w, h)
        tracker = cv2.legacy.TrackerKCF_create()  # Use KCF tracker
        trackers1[person_id_counter1] = tracker
        person_id1 = person_id_counter1
        person_id_counter1 += 1
        person_ids1.add(person_id1)

    # Iterate over detected upper bodies for the second webcam
    for (x, y, w, h) in upper_bodies2:
        # Create a new tracker for each detected person
        bbox = (x, y, w, h)
        tracker = cv2.legacy.TrackerKCF_create()  # Use KCF tracker
        trackers2[person_id_counter2] = tracker
        person_id2 = person_id_counter2
        person_id_counter2 += 1
        person_ids2.add(person_id2)

    # Log timestamp and detection count every five minutes
    current_time = datetime.now()
    if (current_time - start_time).seconds >= 300:  # Check every 5 minutes
        # Only log if there are new detections
        if len(person_ids1) > 0 or len(person_ids2) > 0:
            excel_data1["Timestamp"].append(start_time.strftime("%Y-%m-%d %H:%M:%S"))
            excel_data1["Detections"].append(len(person_ids1))

            excel_data2["Timestamp"].append(start_time.strftime("%Y-%m-%d %H:%M:%S"))
            excel_data2["Detections"].append(len(person_ids2))

            # Write data to Excel file inside the "Total-Detection" folder on the desktop for camera 1
            with pd.ExcelWriter(excel_file_path1, engine='openpyxl', mode='a') as writer:
                df1 = pd.DataFrame(excel_data1)
                df1.to_excel(writer, index=False, sheet_name='Sheet1', startrow=writer.sheets['Sheet1'].max_row, header=False)
                print(f"Saved {excel_file_path1}")

            # Write data to Excel file inside the "Total-Detection" folder on the desktop for camera 2
            with pd.ExcelWriter(excel_file_path2, engine='openpyxl', mode='a') as writer:
                df2 = pd.DataFrame(excel_data2)
                df2.to_excel(writer, index=False, sheet_name='Sheet1', startrow=writer.sheets['Sheet1'].max_row, header=False)
                print(f"Saved {excel_file_path2}")

        # Reset counters for the next 5 minutes
        person_ids1.clear()
        person_ids2.clear()
        start_time = datetime.now()

    # Display "System Online" with a green box around the tracked person for the first webcam
    cv2.putText(frame1, "System Online", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.imshow("Camera 1", frame1)

    # Display "System Online" with a green box around the tracked person for the second webcam
    cv2.putText(frame2, "System Online", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.imshow("Camera 2", frame2)

    # Check for the 'q' key to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video captures
cap1.release()
cap2.release()

# Close any open windows
cv2.destroyAllWindows()
