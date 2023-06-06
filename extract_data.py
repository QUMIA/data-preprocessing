# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import pyreadstat

import hashlib
import binascii


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

def read_file(path):
    df = pd.read_spss(path)
    # Make patient id 7-character strings
    df['MDN'] = df['MDN'].astype(int).astype(str).str.zfill(7)
    return df

def pseudonymize_ids(df, salt):
    df['anon_id'] = df.apply(lambda row: pseudonymize_id(row, salt), axis=1)

def pseudonymize_id(row, salt):
    patient_id = row['MDN']
    bin_hash = hashlib.pbkdf2_hmac('sha256', patient_id.encode('utf-8'),
                               salt.encode('utf-8'), 100) #TODO 100000
    return binascii.hexlify(bin_hash).decode('utf-8')

def write_file(path, df):
    df.to_csv(path, index=False)

def create_output_df(data):
    return pd.DataFrame(columns=['anon_id', 'Age_exam', 'Sex', 'Weight', 'Length', 'BMI',
                    'muscle', 'side', 'z_score', 'h_score', 'image_index'], data=data)

def get_output_row(row_in, muscle, side, image_index, missing_muscles):
    muscle_abrev = mapping.get(muscle)
    if muscle_abrev == None:
        missing_muscles.add(muscle)
    anon_columns = ['anon_id', 'Age_exam', 'Sex', 'Weight', 'Length', 'BMI']
    row_vals = row_in[anon_columns].to_dict()
    row_vals['muscle'] = muscle_abrev
    row_vals['side'] = side
    row_vals['image_index'] = image_index
    return row_vals

