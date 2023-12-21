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

# This maps the old categories (used in 0-500 file, column "Diagnosis_categorized")
# to the new categories
diagnosis_mapping = [0, 99, 5, 1, 5, 5, 5, 2, 3, 3, 4, 3, 5, 5, 99]

# The new category labels (included for completeness)
diagnosis_labels = {
    0: "No NMD",
    1: "spinal muscular atrophies or motor neuron",
    2: "motor nerve roots",
    3: "peripheral nerve",
    4: "neuromuscular transmission",
    5: "myopathy",
    6: "Supraspinal tonal regulation/mimics",
    99: "unknown/uncertain"
}

sex_mapping = {0: 'male', 1: 'female'}

def read_file(path, salt):
    df = pd.read_spss(path, convert_categoricals=False)
    
    # Use labels for sex
    df['Sex'] = df['Sex'].astype(int).map(sex_mapping)
    
    # Make patient id 7-character strings
    df['MDN'] = df['MDN'].astype(int).astype(str).str.zfill(7)
    
    # Pseudonymize ids (adds column)
    df['anon_id'] = df.apply(lambda row: pseudonymize_id(row['MDN'], salt), axis=1)
    
    # Add a separate id for exam
    df['exam_id'] = df.apply(
        lambda row: pseudonymize_id(f"{row['MDN']}_{row['Date_exam']}", salt)
        if 'Date_exam' in row
        else row['anon_id'], axis=1)
    
    # Scale length from cm to meters if needed
    if df['Length'].mean() > 10:
        df['Length'] = df['Length'] / 100

    return df

def pseudonymize_id(patient_id, salt):
    bin_hash = hashlib.pbkdf2_hmac('sha256', patient_id.encode('utf-8'),
                               salt.encode('utf-8'), 1000)
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
    return pd.DataFrame(columns=['anon_id', 'exam_id', 'Age_exam', 'Sex', 'Weight', 'Length',
                    'diagnosis', 'muscle', 'side', 'z_score', 'h_score', 'image_file', 'has_markers',
                    'li_x', 'li_y', 're_x', 're_y', 'id_x', 'id_y'], data=data)

def get_output_row(row_in, muscle, side, image_file):
    """ Combines data from
        * the original row (anonymous id, personal attributes considered anonymous)
        * the selected muscle + side
        * the file name of the image being written
        * the H and z score for the selected muscle
    """
    # Discard entries with possibly identifying properties
    if row_in['Length'] >= 2.0:
        raise Exception("High length")
    if row_in['Weight'] >= 150.0:
        raise Exception("High weight")

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
    
    # Diagnosis
    diagnosis = -1
    if "Diagnosis_categorized_step_1" in row_in:
        diagnosis = int(row_in['Diagnosis_categorized_step_1'])
    if "Diagnosis_categorized" in row_in:
        diagnosis = diagnosis_mapping[int(row_in['Diagnosis_categorized'])]
    
    # Copy data
    anon_columns = ['anon_id', 'exam_id', 'Age_exam', 'Sex', 'Weight', 'Length']
    row_out = row_in[anon_columns].to_dict()
    row_out['diagnosis'] = diagnosis
    row_out['muscle'] = muscle_abbrev
    row_out['side'] = side
    row_out['z_score'] = z_score
    row_out['h_score'] = h_score
    row_out['image_file'] = image_file
    return row_out
