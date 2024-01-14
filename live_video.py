import cv2

def main():
    # Set up video capture
    video_capture = cv2.VideoCapture(0)  # Use index 0 for the first webcam

    # Check if the video capture is successfully opened
    if not video_capture.isOpened():
        print("Failed to open webcam")
        return

    while True:
        # Read a frame from the webcam
        ret, frame = video_capture.read()

        # Display the frame in a window named "Live Video"
        cv2.imshow('Live Video', frame)

        # Check for the 'q' key to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close any open windows
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
