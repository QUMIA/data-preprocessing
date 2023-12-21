# -*- coding: utf-8 -*-
"""
"""

import pydicom
from pydicom.pixel_data_handlers.util import convert_color_space
import cv2
import numpy as np
import os


# Read the templates and masks
templates = files = [
    ('template_LI.png', 'mask_LI.png'),
    ('template_RE.png', 'mask_RE.png'),
    ('template_ID.png', 'mask_ID.png'),
    ('template_marker.png', 'mask_marker.png')]
read_file = lambda x: cv2.imread(os.path.join('template-matching', x), cv2.IMREAD_GRAYSCALE)
template_imgs = [(read_file(item[0]), read_file(item[1])) for item in files]

                  
def convert_image(file_in, file_out, row_out, do_write):
    
    # read dicom image
    ds = pydicom.read_file(file_in)
    
    # print tags
#    for element in ds:
#        print(element)
        
    # get image data
    img = ds.pixel_array
    
    # convert to RGB, then to grayscale
    img_rgb = convert_color_space(img, 'YBR_FULL_422', 'RGB')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    
    # retrieve region with actual image data
    region_data = ds[(0x0018, 0x6011)] # Sequence of Ultrasound Regions
    for item in region_data:
        x0 = get_value_from_sequence(item, (0x0018, 0x6018)) # Region Location Min X0
        y0 = get_value_from_sequence(item, (0x0018, 0x601a)) # Region Location Min Y0
        x1 = get_value_from_sequence(item, (0x0018, 0x601c)) # Region Location Min X1
        y1 = get_value_from_sequence(item, (0x0018, 0x601e)) # Region Location Min Y1 
    
    # Tighten crop region: clip off burnt-in rulers to the right and bottom
    x0 += 0
    y0 += 0
    x1 -= 32
    y1 -= 6  # only crop the ruler, not the muscle name yet
    img_crop1 = img_gray[y0:y1, x0:x1]

    # Crop black borders and burnt-in logo
    threshold = 10
    rows = np.where(np.mean(img_crop1, 0) > threshold)[0]
    if rows.size:
        cols = np.where(np.mean(img_crop1, 1) > threshold)[0]
        img_crop2 = img_crop1[cols[0]: cols[-1] + 1, rows[0]: rows[-1] + 1]
    else:
        img_crop2 = img_crop1[:1, :1]

    # Check for burnt-in prints
    tm_result_li = find_template(img_crop2, template_imgs[0])
    tm_result_re = find_template(img_crop2, template_imgs[1])
    tm_result_id = find_template(img_crop2, template_imgs[2])
    tm_result_markers = find_template(img_crop2, template_imgs[3])

    # Crop depending on result
    has_markers = tm_result_markers[0]
    row_out['has_markers'] = has_markers
    row_out['li_x'], row_out['li_y'] = tm_result_li[1] if tm_result_li[0] else (-1, -1)
    row_out['re_x'], row_out['re_y'] = tm_result_re[1] if tm_result_re[0] else (-1, -1)
    row_out['id_x'], row_out['id_y'] = tm_result_id[1] if tm_result_id[0] else (-1, -1)

    # write image
    if do_write:
        cv2.imwrite(file_out, img_crop2)


def find_template(search_img, template_img_pair):
    template_img = template_img_pair[0]
    mask_img = template_img_pair[1]
    
    # Perform template matching with the mask
    result = cv2.matchTemplate(search_img, template_img, cv2.TM_SQDIFF, mask=mask_img)

    # Get the minimum and maximum values, and their corresponding positions
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    threshold = 30000
    return (min_val < threshold, min_loc)


def get_value_from_sequence(item, tag):
    data = item.get(tag)
    if data is not None:
        return data.value
    