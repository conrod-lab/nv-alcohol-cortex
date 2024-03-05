#This script uses neuromaps https://netneurolab.github.io/neuromaps/installation.html
# Python 3.7+
# Note: the human connectome workbench must be installed and 
# available from the command line
# https://www.humanconnectome.org/software/get-connectome-workbench

#pip install git+https://github.com/netneurolab/netneurotools
#pip install git+https://github.com/netneurolab/neuromaps

import numpy as np
import pandas as pd
import os
import neuromaps
from neuromaps import datasets, parcellate, images, transforms
from netneurotools import datasets as nnt_datasets

# define path
base_path = os.path.dirname(os.getcwd())

# Fetch parcellation files for MNI and fsaverage
# PET files are in MNI (1mm or 3mm) and fsaverage 164k density, which is fsaverage from nnt

from netneurotools.datasets.fetchers import fetch_cammoun2012

cammoun_mni_parc = fetch_cammoun2012(version='MNI152NLin2009aSym', data_dir=os.path.join(base_path, 'temp'), url=None,
                     resume=True, verbose=1)
cammoun_033_mni_parc = cammoun_mni_parc.scale033

cammoun_fs164k_parc = fetch_cammoun2012(version='fsaverage', data_dir=os.path.join(base_path, 'temp'), url=None,
                                resume=True, verbose=1)
cammoun_fs164k_parc_scale_033 = cammoun_fs164k_parc.scale033
cammoun_033_fs164k_parc = images.annot_to_gifti(cammoun_fs164k_parc_scale_033)

import os
os.environ['PATH'] += ':/Applications/workbench/bin_macosx64'


from neuromaps import resampling
cammoun_033_mni_parc, cammoun_033_fs164k_parc = resampling.resample_images(src=cammoun_033_mni_parc, trg=cammoun_033_fs164k_parc,
                                            src_space='MNI152',
                                            trg_space='fsaverage',
                                            resampling='transform_to_alt',
                                            alt_spec=('fsaverage', '10k'))

from neuromaps import stats
corr = stats.compare_images(cammoun_033_mni_parc, cammoun_033_fs164k_parc)
print(f'Correlation: r = {corr:.02f}')

annot_pet_all = list(datasets.available_annotations(tags='PET'))

# Each PET image has only one source*desc combination
annot_pet = [item for item in annot_pet_all if not ('beliveau2017' in item and 'MNI152' in item)]
annot_pet = [item for item in annot_pet if not ('norgaard2021' in item and 'MNI152' in item)]
annot_pet = [item for item in annot_pet if not ('raichle' in item)]

# Parcellate PET images

# All PET images are in MNI152 except for beliveau2017 and norgaard2021, which are fsaverage and 164k

# initialize
parc_pet = dict([])

# go over each annotation and parcellate depending on the space 
for (src, desc, space, den) in annot_pet:

    annot = datasets.fetch_annotation(source=src, desc=desc, space=space, den=den)
    
    if space == 'MNI152':
        parcellater = parcellate.Parcellater(cammoun_033_mni_parc, 'MNI152')
    elif space == 'fsaverage':
        parcellater = parcellate.Parcellater(cammoun_033_fs164k_parc, 'fsaverage')

    parc_pet[desc, src] = parcellater.fit_transform(annot, space=space, ignore_background_data=True)

    parc_pet[desc, src] = parc_pet[desc, src][0]

import csv

# Output folder
#out_folder = 'parc_pet_dk_test'
out_folder_name = 'parc_pet_dk'
out_folder = os.path.join(base_path, 'temp', out_folder_name)
if not os.path.exists(out_folder):
  os.makedirs(out_folder)

for key, value in parc_pet.items():
  desc, src = key
  filename = f"{desc}_{src}_dk_nnt.csv"
  out_path = os.path.join(out_folder, filename)

  with open(out_path, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(value) 
    
print("CSV files exported")
