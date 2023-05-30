# -*- coding: utf-8 -*-
"""
"""

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import os
import glob
from extract_data import read_file, anonymize_id, extract_data, write_file
from extract_images import convert_image
import scipy.io

def main():
    
    input_file = os.environ["QU_INPUT"]
    output_file = os.environ["QU_OUTPUT"]
    img_in_dir = os.environ["QU_IMG_IN_DIR"]
    img_out_dir = os.environ["QU_IMG_OUT_DIR"]
    salt = os.environ["QU_SALT"]
    print(input_file, output_file, img_in_dir, img_out_dir)
    
    # Read specified SPSS file
    df = read_file(input_file)
    df['MDN'] = df['MDN'].astype(int).astype(str)

    # Pseudonymize patient ids
    def anonymize_it(row):
        return anonymize_id(row, salt)
    df['anon_id'] = df.apply(anonymize_it, axis=1)
    
    # Loop through all entries to process
    no_images_count = 0
    for index, row in df.iterrows():
        if index > 9: break # For development, limit the number of entries processed
        
        # Determine location of image data
        patient_id = row['MDN']
        pattern = '/'.join([img_in_dir, patient_id + '_*'])
        folder_names = glob.glob(pattern)
        #TODO: check for multiple / how to relate multiple visits (images) to db entry?
        if len(folder_names) == 0:
            print("No images found for ", patient_id)
            no_images_count += 1
            continue
        visit_img_dir = os.path.join(img_in_dir, folder_names[0])

        # Create output dir if needed
        visit_out_dir = os.path.join(img_out_dir, row['anon_id'])
        if not os.path.exists(visit_out_dir):
            os.mkdir(visit_out_dir)

        # Loop through all images by looking at the .mat files in de /roi folder
        file_list = glob.glob(os.path.join(visit_img_dir, "roi", "*.dcm.mat"))
        file_list.sort()
        index = 0
        for f in file_list:
            print(f)
            mat = scipy.io.loadmat(f)
            print(mat['muscle'])
            file_name = os.path.split(f)[1]
            file_in = os.path.join(visit_img_dir, file_name.replace('.dcm.mat', '.dcm'))
            file_out = os.path.join(visit_out_dir, f"{str(index).zfill(2)}.png")
            convert_image(file_in, file_out)
            index += 1
    
    print(f"Couldn't find images for {no_images_count} of {index} entries")

    # Extract anonymized data from SPSS data and save as csv
    df_anon = extract_data(df)
    write_file(output_file, df_anon)
    print(f"Data written to {output_file}")
    
    
if __name__ == "__main__":
    main()
    
