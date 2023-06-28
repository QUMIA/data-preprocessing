# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import pyreadstat

import hashlib
import binascii
import glob


mapping = {
    "Masseter": "Masseter",
    "Digastricus": "Digastric",
    "Geniohyoideus": "Geniohyoid",
    "Sterno cleido": "SCM",
    "Trapezius": "Trap",
    "Deltoideus": "Deltoid",
    "Biceps brachii": "Biceps",
    "Flexor carpi radialis": "FCR",
    "Extensors underarm": "Extensors",
    "Interosseus dorsalis I": "ID1",
    "Rectus abdominis": "Rectusab",
    "Rectus femoris": "RF",
    "Vastus lateralis": "VL",
    "Tibialis anterior": "TA",
    "Gastrocnemius medial head": "GM",
    "Peroneus tertius": "PerT"
}

def read_file(path, salt):
    df = pd.read_spss(path)
    
    # Make patient id 7-character strings
    df['MDN'] = df['MDN'].astype(int).astype(str).str.zfill(7)
    
    # Pseudonymize ids (adds column)
    df['anon_id'] = df.apply(lambda row: pseudonymize_id(row['MDN'], salt), axis=1)
    
    # Add a separate id for exam
    df['exam_id'] = df.apply(
        lambda row: pseudonymize_id(f"{row['MDN']}_{row['Date_exam']}", salt)
        if 'Date_exam' in row
        else row['anon_id'], axis=1)
    
    return df

def pseudonymize_id(patient_id, salt):
    bin_hash = hashlib.pbkdf2_hmac('sha256', patient_id.encode('utf-8'),
                               salt.encode('utf-8'), 100) #TODO 100000
    return binascii.hexlify(bin_hash).decode('utf-8')[0:32]

def get_image_folder_names(row, img_in_dir):
    patient_id = row['MDN']
    if 'Date_exam' in row:
        format_exam_date = row['Date_exam'].strftime('%Y%m%d')
        pattern = '/'.join([img_in_dir, f'{patient_id}_{format_exam_date}*'])
    else:
        pattern = '/'.join([img_in_dir, f'{patient_id}_*'])
    return glob.glob(pattern)

def create_output_df(data):
    return pd.DataFrame(columns=['anon_id', 'exam_id', 'Age_exam', 'Sex', 'Weight', 'Length', 'Final_diagnosis',
                    'muscle', 'side', 'z_score', 'h_score', 'image_file'], data=data)

def get_output_row(row_in, muscle, side, image_file):
    """ Combines data from
        * the original row (anonymous id, personal attributes considered anonymous)
        * the selected muscle + side
        * the file name of the image being written
        * the H and z score for the selected muscle
    """
    # Map muscle name
    muscle_abbrev = mapping.get(muscle)
    if muscle_abbrev == None:
        return None
    # Obligatory special case
    if muscle_abbrev == "Geniohyoid":
        side = "" # ignore the side (it has none in the SPSS file)
    
    # H/z-score
    z_score = row_in[f'{muscle_abbrev}{side}_z']
    h_score = row_in[f'{muscle_abbrev}{side}_H']
    if pd.isna(z_score) or pd.isna(h_score):
        raise Exception("Missing z/h-score")
    
    # Copy data
    anon_columns = ['anon_id', 'exam_id', 'Age_exam', 'Sex', 'Weight', 'Length', 'Final_diagnosis']
    row_out = row_in[anon_columns].to_dict()
    row_out['muscle'] = muscle_abbrev
    row_out['side'] = side
    row_out['z_score'] = z_score
    row_out['h_score'] = h_score
    row_out['image_file'] = image_file
    return row_out
