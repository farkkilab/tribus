import pandas as pd
import os
import numpy as np
import sys
import glob
import re
import json
import umap
from numpy.random import MT19937
from numpy.random import RandomState, SeedSequence


# Hardcoded celltype column

CTC = "GlobalCellType"

# Hardcoded iteration name
ITER = "Test"

# Get the folder path from command line arguments
# e.g. tribus report command would run "python process_data.py PATH"
arg = sys.argv[1]

# Get the files from PATH/*.csv
# TODO:Change in future to work with tribus folder structure
files=glob.glob(arg+"\*.csv")


if(len(files)==0):
    sys.exit("No .csv files found in "+arg)

# Destination path is a sister directory for the input folder called plot_data
destpath = re.sub('/[^/]+$', '',arg) +"/plot_data/"
# Get the --gates-- /PHENOTYPE PROFILES/
phprof = dict()

# The old gate format. This parses it line by line
f = open(arg+"/gates.R")

currname = ''
currpos = []
currneg = []

for line in f:
    # Cell type names are surrounded by [[]]
    name = re.search('\[\[.*\]\]',line)
    if name != None:
        currname = re.sub('[\[\]\"]','',name.group())
        continue
    if re.search('Pos=',line) != None:
        currpos = re.findall("\'.*\'",line)
        if len(currpos)>0:
            currpos = re.sub("\'",'',currpos[0]).split(",")
        continue
    if re.search('Neg=',line) != None:
        currneg = re.findall("\'.*\'",line)
        if len(currneg)>0:
            currneg = re.sub("\'",'',currneg[0]).split(",")
    if currname == '':
        continue
    phprof[currname] = {'pos':currpos, 'neg':currneg}
    currname = ''
    currpos = []
    currneg = []

f.close()
# Now we have a dict of dicts that has the "PhP" >:D logic in it
# The others cell type might have the 
# Neg=unique(unlist(lapply(global.gates, function(x) x$Pos)))),
# which means that they are meant to have all other positive markers as neg
# This is not considered now

# Take the pos and neg markers into their own lists and flatten
# In some cases leading whitespaces might occur, so they are trimmed
posmarkers = [phprof[ct]['pos'] for ct in phprof]
posmarkers = [pm.strip() for sl in posmarkers for pm in sl]
negmarkers = [phprof[ct]['neg'] for ct in phprof]
negmarkers = [nm.strip() for sl in negmarkers for nm in sl]

# All unique markers
allmarkers = list(set(posmarkers + negmarkers))

colstoread = ["ID", CTC] + allmarkers

# Operate on all the samples
# this could be separated to a function to make the code more readable

alldata = pd.DataFrame()
dflist = list()

for file in files:
    # Read only markers in PhP. In the test data, sep is whitespace and not comma
    df = pd.read_csv(file, sep=" ", usecols=colstoread)
    # Get the filenames
    filename = re.sub("\.csv","",os.path.basename(file))
    # Get the unique celltypes
    # Also known from names in phprof
    ct = [ct for ct in df[CTC].unique()]
    # Means by cell type
    meansbyct = df.groupby(CTC).mean()
    varsbyct = df.groupby(CTC).var()
    varsbyct = varsbyct.rename(lambda cn: cn+"_var",axis=1)
    # T-test between celltypes
    # Turns out to be not that informative as difference between means 11.741 and 11.744
    # is significant due to the large sample size. Even with multiple hypothesis correction
    #data = []
    #for i in range(0,len(ct)):
    #    for j in range(i+1,len(ct)):
    #        for marker in allmarkers:
    #            cells1 = df.where(df[CTC]==ct[i]).dropna()[marker]
    #            cells2 = df.where(df[CTC]==ct[j]).dropna()[marker]
    #            # tres = scipy.stats.ttest_ind(cells1,cells2, equal_var=False)
    #            tres = scipy.stats.kruskal(cells1,cells2)
    #            # Lazily add the result twice so it doesn't matter which cell type is searched
    #            # as the first cell and which as the second
    #            data.append([ct[i],ct[j],marker,tres])
    #            data.append([ct[j],ct[i],marker,tres])
    #
    #ttest = pd.DataFrame(data, columns=["Cell 1", "Cell 2", "Marker", "t-test"])
    # Multiple hypothesis correction could be done by
    # mt.multipletests(pvals, 0.05, method="fdr_bh")
    # Combine means and variances to a heatmap data frame
    heatmap_export = meansbyct
    heatmap_export["celltype"] = list(heatmap_export.index)
    heatmap_export = pd.concat([heatmap_export,varsbyct] ,axis=1)
    heatmap_export = heatmap_export.drop(columns=["ID","ID_var"])
    exp = json.loads(heatmap_export.to_json(orient="records"))
    with open(destpath+filename+'_heatmapdata.json', 'w') as f:
        json.dump(exp, f)
    ct_counts = df[CTC].value_counts()
    l = list(ct_counts.index)
    ct_dict_list = [{"id":l[i],"label":l[i],"value":str(ct_counts[i])} for i in range(0,len(ct_counts))]
    with open(destpath+filename+'_piechartdata.json', 'w') as f:
        json.dump(ct_dict_list, f)
    df["Sample"] = filename
    dflist.append(df)
    
# After loop combine dataframes
# This is to compute the umap etc
alldata = pd.concat(dflist)

# This WILL be computationally intensive and eat your memory
# User would benefit from having an external machine (=server)
# doing the calculations.
# Otherwise HEAVY subsampling is needed
rs = RandomState(MT19937(SeedSequence(133131313113)))

# Leave only relevant info as umap input
usubset = alldata.sample(n=10000)
udata = np.array(usubset.drop(columns=["ID", "Sample",CTC]),dtype=np.float64)
# Target classes apparently need to be integers/numerical
a,target = np.unique(np.array(usubset[CTC]),return_inverse=True)
umap_res = umap.UMAP().fit_transform(udata,y=target)

# Construct the output for umap scatterplot
ures = pd.DataFrame(data={"X":umap_res[:,0], "Y":umap_res[:,1]})
ures.index = usubset.index
ures = pd.concat([ures,usubset[["ID",CTC,"Sample"]]],axis=1)

# TODO: Add the ID and Sample values to the data to facilitate color changing in the js side
umapdict = [{"id":ict, "data": [{"x":row["X"],"y":row["Y"]} for index, row in ures.where(ures[CTC]==ict).dropna().iterrows()]} for ict in ures[CTC].unique()]

with open(destpath+ITER+'_umapdata.json', 'w') as f:
    json.dump(umapdict, f)