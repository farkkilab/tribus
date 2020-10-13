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

def filter_markers(cell_data_table,table,level):
    cell_data = pd.read_csv(cell_data_table)
    cell_data.columns = cell_data.columns.str.lower()
    dc_casefold = [item.casefold() for item in cell_data.columns]
    used_markers = get_markers(table,level)
    um_casefold = [i.casefold() for i in used_markers]
    d_used = cell_data[sorted(set(dc_casefold).intersection(um_casefold), key=dc_casefold.index)]
    
    return(d_used)

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
