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
    for element in ds:
        print(element)
        
    # get image data
    img = ds.pixel_array
    
    # convert to RGB
    img_rgb = convert_color_space(img, 'YBR_FULL_422', 'RGB')
    
    # write image
    cv2.imwrite(file_out, img_rgb)
