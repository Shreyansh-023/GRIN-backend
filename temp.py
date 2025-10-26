import cv2
import os
import sys

def crop_face(image_path, output_path="cropped_face.jpg", expand_ratio=0.3):
    """
    Detects a face and crops a larger region including hair and chin.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the cropped face image.
        expand_ratio (float): Fraction by which to expand the detected face bounding box.
                              0.3 = expand 30% in each direction.
    """
    # Check if image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Load the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load OpenCV's Haar cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

    if len(faces) == 0:
        raise ValueError("No face detected in the image.")

    # Choose the largest detected face (most likely the main subject)
    x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]

    # Expand the bounding box to include hair, chin, and sides
    h_expand = int(h * expand_ratio)
    w_expand = int(w * expand_ratio)

    x1 = max(x - w_expand, 0)
    y1 = max(y - h_expand, 0)
    x2 = min(x + w + w_expand, image.shape[1])
    y2 = min(y + h + h_expand, image.shape[0])

    # Crop expanded region
    cropped_face = image[y1:y2, x1:x2]

    # Save cropped face
    cv2.imwrite(output_path, cropped_face)

    print(f"✅ Face cropped (with hair/chin) and saved as: {output_path}")
    return output_path


# Example usage
if __name__ == "__main__":
    try:
        crop_face("download.jpg", "output_face.jpg", expand_ratio=0.3)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)