# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import pyreadstat

import hashlib
import binascii


def read_file(path):
    return pd.read_spss(path)

def anonymize_id(row, salt):
    patient_id = str(int(row['MDN']))
    bin_hash = hashlib.pbkdf2_hmac('sha256', patient_id.encode('utf-8'),
                               salt.encode('utf-8'), 100000)
    return binascii.hexlify(bin_hash).decode('utf-8')

def extract_data(df_in):
    anon_columns = ['anon_id', 'Age_exam', 'Sex', 'Weight', 'Length', 'BMI']
    df_out = df_in[anon_columns]
    return df_out

def write_file(path, df):
    df.to_csv(path, index=False)
