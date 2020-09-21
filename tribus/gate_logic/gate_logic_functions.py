import numpy as np
import pandas as pd

def get_celltypes(table,level):
    df = pd.ExcelFile(table)
    data = pd.read_excel(df, df.sheet_names, index_col='Marker')   
    celltype_list = list(data[level].columns)
    
    return celltype_list

def get_markers(table,level):
    df = pd.ExcelFile(table)
    data = pd.read_excel(df, df.sheet_names, index_col='Marker') 
    used_markers = []

    for k in range(len(data[level].index)):
        s = list(data[level].loc[data[level].index[k]])
        if data[level].index[k] not in used_markers and 1 in s or data[level].index[k] not in used_markers and -1 in s:
            used_markers.append(data[level].index[k])
            
    return(used_markers)

def get_gates(table,level):
    df = pd.ExcelFile(table)
    data = pd.read_excel(df, df.sheet_names, index_col='Marker')   
    celltypes = list(data[level].columns)
    all_neg_mark = []
    all_pos_mark = []
    
    for i in range(len(celltypes)):
        neg_mark = list(data[level][celltypes[i]].loc[lambda s: s == -1].index)
        all_neg_mark.append(neg_mark)
        
    for j in range(len(celltypes)):
        pos_mark = list(data[level][celltypes[j]].loc[lambda s: s == 1].index)
        all_pos_mark.append(pos_mark)
    
    d = {'celltype': celltypes, 'positive': all_pos_mark, 'negative': all_neg_mark}
    df = pd.DataFrame(data=d,)
    df_indexed = df.set_index('celltype')
        
    return df_indexed
