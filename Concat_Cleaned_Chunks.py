#!/usr/bin/env python
# coding: utf-8

# # Concat Cleaned Files

# The purpose of this script is to concatenate all cleaned HMDA files into one.

import pandas as pd
import glob
import os
import numpy as np

# setting the path for joining multiple files
files2019 = os.path.join("2019_clean_chunks", "2019_chunk**.csv")

# list of merged files returned
files2019 = glob.glob(files2019)

print("Resultant CSV after joining all CSV files at a particular location...");

# joining files with concat and read_csv
df2019 = pd.concat(map(pd.read_csv, files2019), ignore_index=True)


# In[ ]:


# setting the path for joining multiple files
files2020 = os.path.join("2020_clean_chunks", "2020_chunk**.csv")

# list of merged files returned
files2020 = glob.glob(files2020)

print("Resultant CSV after joining all CSV files at a particular location...");

# joining files with concat and read_csv
df2020 = pd.concat(map(pd.read_csv, files2020), ignore_index=True)


# In[ ]:


# setting the path for joining multiple files
files2021 = os.path.join("2021_clean_chunks", "2021_chunk**.csv")

# list of merged files returned
files2021 = glob.glob(files2021)

print("Resultant CSV after joining all CSV files at a particular location...");

# joining files with concat and read_csv
df2021 = pd.concat(map(pd.read_csv, files2021), ignore_index=True)


# In[ ]:


merged_df = pd.concat([df2019,df2020,df2021])
merged_df.to_csv('HMDA_Cleaned_192021', index=False)

