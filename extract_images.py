# -*- coding: utf-8 -*-
"""
"""

import pydicom
from pydicom.pixel_data_handlers.util import convert_color_space
import cv2


def convert_image(file_in, file_out):
    
    # read dicom image
    ds = pydicom.read_file(file_in)
    
    # print tags
#    for element in ds:
#        print(element)
        
    # get image data
    img = ds.pixel_array
    
    # convert to RGB
    img_rgb = convert_color_space(img, 'YBR_FULL_422', 'RGB')
    
    # retrieve region with actual image data
    region_data = ds[(0x0018, 0x6011)] # Sequence of Ultrasound Regions
    for item in region_data:
        x0 = get_value_from_sequence(item, (0x0018, 0x6018)) # Region Location Min X0
        y0 = get_value_from_sequence(item, (0x0018, 0x601a)) # Region Location Min Y0
        x1 = get_value_from_sequence(item, (0x0018, 0x601c)) # Region Location Min X1
        y1 = get_value_from_sequence(item, (0x0018, 0x601e)) # Region Location Min Y1 
    # print(x0, y0, x1, y1)
   
    # crop image to region
    img_cropped = img_rgb[y0:y1, x0:x1]
    
    # write image
    cv2.imwrite(file_out, img_cropped)

def get_value_from_sequence(item, tag):
    data = item.get(tag)
    if data is not None:
        return data.value
    