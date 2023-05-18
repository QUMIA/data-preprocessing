# -*- coding: utf-8 -*-
"""
"""

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import os
import glob
from extract_data import read_file, anonymize_id, extract_data, write_file
from extract_images import convert_image


def main():
    
    input_file = os.environ["QU_INPUT"]
    output_file = os.environ["QU_OUTPUT"]
    img_in_dir = os.environ["QU_IMG_IN_DIR"]
    img_out_dir = os.environ["QU_IMG_OUT_DIR"]
    salt = os.environ["QU_SALT"]
    
    
    # Read specified SPSS file
    df = read_file(input_file)

    # Replace all patient ids
    def anonymize_it(row):
        anonymize_id(row, salt)
    df['anon_id'] = df.apply(anonymize_it, axis=1)
    
    # Extract anonymized data from SPSS data and save it
    df_anon = extract_data(df)
    write_file(output_file, df_anon)
    
    return
    
    
    # Loop through all entries of original data
    #sfor index, row in df.iterrows():
        
    
    # Determine location of image data
    folder_names = glob.glob(os.path.join(img_in_dir, patient_id + '*'))
    #TODO: check for multiple
    img_dir = os.path.join(img_in_dir, folder_names[0])
    
    # Loop through selected images
    # Only select the images that have an associated .tif image (but read the dicom)
    file_list = glob.glob(os.path.join(img_dir, "*.tif"))
    for f in file_list:
        print(f)
        file = os.path.split(f)[1]
        file_in = file.replace('.tif', '.dcm')
        file_out = file.replace('.tif', '.png')
        #convert_image(img_file_in, img_file_out)
    
    
if __name__ == "__main__":
    main()
    
