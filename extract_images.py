# -*- coding: utf-8 -*-
"""
"""

import pydicom
from pydicom.pixel_data_handlers.util import convert_color_space
import cv2
import numpy as np


def convert_image(file_in, file_out):
    
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
    
    # Tighten crop region (clip off as much burnt-in annotations as possible)
    x0 += 0
    y0 += 0
    x1 -= 32
    y1 -= 65
   
    # Crop image to region
    img_crop1 = img_gray[y0:y1, x0:x1]

    # Crop black borders and burnt-in logo
    threshold = 10
    rows = np.where(np.mean(img_crop1, 0) > threshold)[0]
    if rows.size:
        cols = np.where(np.mean(img_crop1, 1) > threshold)[0]
        img_crop2 = img_crop1[cols[0]: cols[-1] + 1, rows[0]: rows[-1] + 1]
    else:
        img_crop2 = img_crop1[:1, :1]
    
    # write image
    cv2.imwrite(file_out, img_crop2)

def get_value_from_sequence(item, tag):
    data = item.get(tag)
    if data is not None:
        return data.value
    