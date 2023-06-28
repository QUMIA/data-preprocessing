# -*- coding: utf-8 -*-
"""
"""

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import os
import glob
import scipy.io
from extract_data import read_file, create_output_df, get_output_row, get_image_folder_names
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
    unique_patients = set()
    count_ambiguous_entries = 0
    count_errors = 0
    count_skipped = 0
    count_images_converted = 0
    count_exams = 0
    
    # Loop through all entries to process
    for index, row_in in df.iterrows():
        #if index >= 100: break # For development, limit the number of entries processed
        print("Processing entry", index)
        
        # Check for possible ambiguity
        patient_id = row_in['MDN']
        if patient_id in unique_patients and not 'Date_exam' in row_in:
            print("Ambiguous entry for", patient_id)
            count_ambiguous_entries += 1
            continue
        
        # Determine directory of image data (based on patient id and exam date)
        folder_names = get_image_folder_names(row_in, img_in_dir)
        if len(folder_names) > 1:
            print("Ambiguous image folders for", patient_id)
            count_ambiguous_image_folders += 1
            continue
        if len(folder_names) == 0:
            print("No images found for ", patient_id)
            no_images_count += 1
            continue
        visit_img_dir = os.path.join(img_in_dir, folder_names[0])

        # Create output dir if needed
        visit_out_dir = os.path.join(img_out_dir, row_in['exam_id'])
        if not os.path.exists(visit_out_dir):
            os.mkdir(visit_out_dir)
            do_skip_img_convert = False
        else:
            # Don't re-process images when output exists (but do output entries to csv)
            count_skipped += 1
            do_skip_img_convert = True

        # Loop through all images by looking at the .mat files in de /roi folder
        file_list = glob.glob(os.path.join(visit_img_dir, "roi", "*.dcm.mat"))
        file_list.sort()
        image_index = 0
        did_process_entry = False
        for f in file_list:
            # Get data from .mat
            mat = scipy.io.loadmat(f)
            muscle = mat['muscle'][0]
            side = mat['side'][0]
            
            output_image_file = f"{str(image_index).zfill(2)}.png"
            
            # Get all the information together
            try:
                row_out = get_output_row(row_in, muscle, side, output_image_file)
            except Exception as e:
                print(f"ERROR: {e} while processing {patient_id} {muscle} {side} {f}")
                count_errors += 1
                continue
                
            # Check if the muscle was found in SPSS data
            if row_out != None:
                # Add to output data
                output_rows.append(row_out)
                unique_patients.add(patient_id)
                did_process_entry = True
                
                # Convert the image
                file_name = os.path.split(f)[1]
                file_in = os.path.join(visit_img_dir, file_name.replace('.dcm.mat', '.dcm'))
                file_out = os.path.join(visit_out_dir, output_image_file)
                if not do_skip_img_convert:
                    convert_image(file_in, file_out)
                    count_images_converted += 1
                    image_index += 1
            else:
                missing_muscles.add(muscle)
                count_missing_muscles += 1
        
        if did_process_entry:
            count_exams += 1
    
    print(f"Couldn't find images for {no_images_count} of {index} entries")
    print(f"Ambiguous image folders for {count_ambiguous_image_folders} entries")
    print(f"Missing muscles ({count_missing_muscles}x) in mapping: {missing_muscles}")
    print(f"Found {count_ambiguous_entries} ambiguous entries in table (without exam date)")
    print(f"{count_errors} errors found extracting table data")
    print(f"{count_skipped} exams skipped because output exists")
    print(f"{count_images_converted} images converted")
    print(f"Entry count: {len(output_rows)} muscles for {count_exams} exams, {len(unique_patients)} patients")
    
    # Write collected output data
    df_out = create_output_df(output_rows)
    df_out.to_csv(output_file, index=False)
    print(f"Data written to {output_file}")
    
    
if __name__ == "__main__":
    main()
    
