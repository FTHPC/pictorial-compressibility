'''
pictoral_template.py
This is template tutorial code for LANL LA-UR-21-32202 
compression performance analysis using libpressio


This template used code snippets from the libpressio_tutorial found here:
https://github.com/FTHPC/libpressio_tutorial

For more information regarding libpressio visit:
https://robertu94.github.io/libpressio/

'''

from pathlib import Path
from logging import raiseExceptions
from csv import DictWriter
from os import path
import matplotlib.pyplot as plt
import numpy as np
import h5py as h5
import libpressio
import itertools
import json
import os



#globals to easily manipulate functionality of template
input_folder=str(Path(__file__).parent.absolute())+"/datasets/LA-UR-21-32202/raw/"
#dtype of images
output_file = "teststats.csv"
#compressors to be ran                    
compressor_list = ["sz", "zfp"]
metrics_keys = [
        'info:compressor',
        'info:bound',
        'size:compression_ratio',
        'composite:compression_rate',
        'error_stat:psnr',
        'error_stat:rmse',
        'error_stat:mse',
    ]                                



'''
Depending on the compressor you use, there are different configurations that need to be set.

Compressors that support the pressio meta compression will work using the config below.
As of 0.79.0, current compressors include: sz, zfp, and mgard

To run other compressors, you need to set the required options
See "pressio -a help [compressor_name]" to find detailed options
https://robertu94.github.io/libpressio/pressiooptions.html
'''
def make_config(compressor_id: str, bound: float, dtype: str):
    '''t
    To run with a value range relative error bound, use "pressio:rel" instead.
    '''
    if compressor_id in ["sz", "mgard", "zfp"]:
        return {"pressio:abs": bound}
    else:
        raise RuntimeError("ERROR: unknown compressor")



def run_compressors(input_data, dtype: str, compressors: list, start=-1, stop=-1):
    decomp_data = input_data.copy()
    try:
        for compressor_id, bound in itertools.product(compressors, [.5, 1]):
            compressor = libpressio.PressioCompressor.from_config({
                # configure which compressor to use
                "compressor_id": compressor_id,
                # configure the set of metrics to be gathered
                "early_config": {
                    compressor_id+":metric": "composite",
                    "composite:plugins": ["time", "size", "error_stat"]
                },
                "compressor_config": make_config(compressor_id, bound, dtype)                    
                })

            # run compressor to determine metrics
            comp_data = compressor.encode(input_data)
            decomp_data = compressor.decode(comp_data, decomp_data)
            libpressio_metrics = compressor.get_metrics()
            

            libpressio_metrics.update({'info:compressor':compressor_id, 'info:bound':bound})
            
            metrics = {}
            
            #Only stores metrics in 'metrics_keys'
            for key in metrics_keys:
                val = libpressio_metrics.get(key)
                if val:
                    metrics.update({key:val})

            #print(json.dumps(libpressio_metrics, indent=4))
            print(json.dumps(metrics, indent=4))

            #A possiblity is to write the data to a .csv file
            writerow(metrics)
    except:
        print(f"ERROR: failed to compress using {compressor_id} at bound {bound}")


def writerow(metrics):
    # Open CSV file in append mode
    # Create a file object for this file
    full_path = str(Path(__file__).parent.absolute() / output_file)
    file_exists = path.isfile(full_path)
    with open(full_path, 'a') as f_object:
        new = DictWriter(f_object, delimiter=',', fieldnames=metrics_keys)
        if not file_exists:
            #only write head first time
            new.writeheader()
       
        new.writerow(metrics)
        f_object.close()



def main():
    for i, files in enumerate(os.listdir(input_folder)):
        print(files)
        if files.startswith('.'):
            continue
        if files.endswith('.tif'):
            input_file_full = input_folder+files
            Vx = plt.imread(input_file_full)
            run_compressors(Vx, Vx.dtype, compressor_list)
    


if __name__ == "__main__":
    main()
