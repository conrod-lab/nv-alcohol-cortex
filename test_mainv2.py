import os
import csv
from neuromaps import datasets, parcellate, images
from netneurotools.datasets.fetchers import fetch_cammoun2012
import pandas as pd
import numpy as np

def filter_noncortex(scale,space, info=None):
    if space == "MNI152":
        info = pd.read_csv(info)
        cortex = info.query(f'scale == @scale & structure == "cortex"')['id']
        cortex = np.array(cortex) - 1  # python indexing    
        return cortex
    else:
        return None   
    
    return filtered_rois_parc

def fetch_parcellation(version, scale, base_path):
    cammoun_parc = fetch_cammoun2012(version=version, data_dir=os.path.join(base_path, 'temp'), url=None,
                                     resume=True, verbose=1)
    return (cammoun_parc.scale033,cammoun_parc['info']) if scale == 'MNI152' else (images.annot_to_gifti(cammoun_parc.scale033), None)

def fetch_filtered_annotations():
    annot_pet_all = list(datasets.available_annotations(tags='PET'))
    unwanted_sources = {'beliveau2017', 'norgaard2021', 'raichle'}
    return [item for item in annot_pet_all if not any(source in item[0] for source in unwanted_sources)]

def parcellate_pet(parc_pet, annot_pet, cammoun_033_mni_parc, cammoun_033_fs164k_parc,info=None):
    for src, desc, space, den in annot_pet:
        annot = datasets.fetch_annotation(source=src, desc=desc, space=space, den=den)
        parcellater = parcellate.Parcellater(cammoun_033_mni_parc if space == 'MNI152' else cammoun_033_fs164k_parc,
                                              space)
        parc_all_rois = parcellater.fit_transform(annot, space=space, ignore_background_data=True)[0]
        # Filter out the subcortex and brainstem ROIs from parc_pet[desc, src]
        if info:
            cortex_rois = filter_noncortex("scale033",space,info)
            parc_pet[desc, src] = parc_all_rois[cortex_rois]

def export_csv_files(parc_pet, base_path):
    out_folder_name = 'parc_pet_dk'
    out_folder = os.path.join(base_path, 'temp', out_folder_name)
    os.makedirs(out_folder, exist_ok=True)

    for key, value in parc_pet.items():
        desc, src = key
        filename = f"{desc}_{src}_dk_nnt.csv"
        out_path = os.path.join(out_folder, filename)

        with open(out_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(value)

def main():
    base_path = os.path.dirname(os.getcwd())
    cammoun_033_mni_parc, info = fetch_parcellation('MNI152NLin2009aSym', 'MNI152', base_path)
    cammoun_033_fs164k_parc, _ = fetch_parcellation('fsaverage', 'fsaverage', base_path)
    annot_pet = fetch_filtered_annotations()
    parc_pet = {}
    parcellate_pet(parc_pet, annot_pet, cammoun_033_mni_parc, cammoun_033_fs164k_parc,info)
    export_csv_files(parc_pet, base_path)
    print("CSV files exported")

if __name__ == "__main__":
    main()
