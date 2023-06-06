# -*- coding: utf-8 -*-
"""
"""

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import os
import glob
import scipy.io
from extract_data import read_file, create_output_df, get_output_row
from extract_images import convert_image

def main():
    
    input_file = os.environ["QU_INPUT"]
    output_file = os.environ["QU_OUTPUT"]
    img_in_dir = os.environ["QU_IMG_IN_DIR"]
    img_out_dir = os.environ["QU_IMG_OUT_DIR"]
    salt = os.environ["QU_SALT"]
    print(input_file, output_file, img_in_dir, img_out_dir)
    
    # Read specified SPSS file and does some preprocessing
    df = read_file(input_file, salt)

    # To collect output
    output_rows = []
    
    # To record some error information
    no_images_count = 0
    count_ambiguous_image_folders = 0
    missing_muscles = set()
    count_missing_muscles = 0
    
    # Loop through all entries to process
    for index, row in df.iterrows():
        if index > 3: break # For development, limit the number of entries processed
        
        # Determine director of image data (based on patient id and exam date)
        patient_id = row['MDN']
        # TODO handle Date_exam not present?
        format_exam_date = row['Date_exam'].strftime('%Y%m%d')
        pattern = '/'.join([img_in_dir, f'{patient_id}_{format_exam_date}*'])
        folder_names = glob.glob(pattern)
        if len(folder_names) > 1:
            print("Ambiguous image folders for", patient_id, format_exam_date)
            count_ambiguous_image_folders += 1
            continue
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
            
            # Add an entry to the output table
            muscle = mat['muscle'][0]
            side = mat['side'][0]
            row_out = get_output_row(row, muscle, side, index)
            
            # Check if the muscle was found in SPSS data
            if row_out != None:
                output_rows.append(row_out)
                
                # Convert the image
                file_name = os.path.split(f)[1]
                file_in = os.path.join(visit_img_dir, file_name.replace('.dcm.mat', '.dcm'))
                file_out = os.path.join(visit_out_dir, f"{str(index).zfill(2)}.png")
                convert_image(file_in, file_out)
                index += 1
            else:
                missing_muscles.add(muscle)
                count_missing_muscles += 1
    
    print(f"Couldn't find images for {no_images_count} of {index} entries")
    print(f"Ambiguous image folders for {count_ambiguous_image_folders} entries")
    print(f"Missing muscles ({count_missing_muscles}x) in mapping: {missing_muscles}")

    # Write collected output data
    df_out = create_output_df(output_rows)
    df_out.to_csv(output_file, index=False)
    print(f"Data written to {output_file}")
    
    
if __name__ == "__main__":
    main()
    
