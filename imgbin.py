from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import os



#globals to easily manipulate functionality of template
input_folder=str(Path(__file__).parent.absolute())+"/datasets/LA-UR-21-32202/raw/"              

def main():
    for i, files in enumerate(os.listdir(input_folder)):
        print(files)
        if files.startswith('.'):
            continue
        if files.endswith('.tif'):
            input_file_full = input_folder+files
            Vx = plt.imread(input_file_full)

        f = open(input_file_full+".f32", "wb")
        f.write(Vx)

if __name__ == "__main__":
    main()
