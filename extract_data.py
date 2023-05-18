# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import pyreadstat
import hashlib


def read_file(path):
    return pd.read_spss(path)

def anonymize_id(row, salt):
    salted_id = str(int(row['MDN'])) + '_' + salt
    print(salted_id, type(salted_id))
    return 'asdf' #hashlib.pbkdf2_hmac('sha256', salted_id.encode('utf-8'), salt, 100000)

def extract_data(df_in):
    anon_columns = ['anon_id', 'Age_exam', 'Sex', 'Weight', 'Length', 'BMI']
    df_out = df_in[anon_columns]
    return df_out

def write_file(path, df):
    df.to_csv(path, index=False)
