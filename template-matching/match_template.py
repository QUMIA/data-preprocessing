import cv2
import os

files = [
    ('template_LI.png', 'mask_LI.png'),
    ('template_RE.png', 'mask_RE.png'),
    ('template_marker.png', 'mask_marker.png')]

# Load the template and search image
templates = [(
    cv2.imread(template_file, cv2.IMREAD_GRAYSCALE),
    cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)) for template_file, mask_file in files]

file_list = os.listdir('data')
file_list.sort()
for file_name in file_list:
    search_img = cv2.imread(f"data/{file_name}", cv2.IMREAD_GRAYSCALE)
    results = []

    for template_img, mask_img in templates:
        # Perform template matching with the mask
        result = cv2.matchTemplate(search_img, template_img, cv2.TM_SQDIFF, mask=mask_img)

        # Get the minimum and maximum values, and their corresponding positions
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Define a threshold (you can adjust this value according to your needs)
        threshold = 30000

        # Check if the maximum value (match) is above the threshold
        #print(f"File: {file_name}, {[min_val, max_val, min_loc, max_loc]}, {min_val < threshold}")
        
        results.append(min_val < threshold)

    print(f"File: {file_name}, {results}")
    # RE 9-20,
    # LI 21-41
