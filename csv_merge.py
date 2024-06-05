import os
import glob
import pandas as pd

#changes the current directory to the specified path
os.chdir(r"C:\Users\ruben.crespo\Documents\02_Ruben_scripts\Python_codigo\im.nca.postprocessing\aggregation.region\vegetation.carbon.stock\tmp\vcs.aggregated.country")

extension = 'csv'
#We create a list. {}= takes the name of the file.csv in format extension
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

#combine all files in the list up to down
# combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])

#combine on the same axis
combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ], axis=1)

#export to csv in working folder
combined_csv.to_csv( "combined.csv", index=False, encoding='utf-8-sig')

print("congratulations, the script is over")