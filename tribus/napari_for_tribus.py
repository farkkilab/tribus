#!/usr/bin/env python
# coding: utf-8


import numpy as np
import tifffile
import skimage
from tifffile import imread
import napari
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from pathlib import Path
from magicgui import event_loop, magicgui
from PyQt5.QtWidgets import QMessageBox, QApplication, QPushButton
import sys
from PyQt5.QtCore import Slot
import enum
import os
from dask_image.imread import imread as daskread

def open_napari():
    with napari.gui_qt():
        viewer = napari.Viewer()

        def open_corepicker():  
            
            @magicgui(call_button='Get Channels', layout='vertical') #to choose directory add:  core_name={'mode' : 'd'}
            def corepicker(core_name=Path(),channel_name_table=Path()):
                global df_name 
                df_name = str(channel_name_table)

                if core_name.suffix == '.tif' or core_name.suffix == '.tiff':
                    if df_name == '.':
                        with tifffile.TiffFile(core_name) as tif:
                            for page in tif.pages:
                                for tag in page.tags:
                                    tag_name, tag_value = tag.name, tag.value

                                image = page.asarray()
                                viewer.add_image(image, visible=False, blending='additive')

                    elif channel_name_table.suffix == '.xlsx' :
                        df = pd.read_excel(df_name)

                        if 'Channel_number' in df.columns and 'Channel_name' in df.columns:
                            df_indexed = df.set_index('Channel_number')
                            i = 0

                            if 'Cycle' in df.columns and 'Fluorochrome' in df.columns:
                                df_indexed['Cycle'] = df_indexed['Cycle'].fillna(-1)
                                df_indexed['Cycle'] = df_indexed['Cycle'].astype(int)
                                df_indexed['Cycle'] = df_indexed['Cycle'].astype(str)
                                df_indexed['Cycle'] = df_indexed['Cycle'].replace('-1', '')
                                df_indexed['Fluorochrome'] = df_indexed['Fluorochrome'].fillna('')


                            with tifffile.TiffFile(core_name) as tif:
                                for page in tif.pages:
                                    channel_name = df_indexed['Channel_name'][i]
                                    if df_indexed.index[i] % 4 == 0:
                                        cmap = 'blue'
                                    elif df_indexed['Channel_name'][i] == 'E-cadherin':
                                        cmap = 'magenta'
                                    elif df_indexed['Channel_name'][i] == 'CD4':
                                        cmap = 'cyan'
                                    elif df_indexed['Channel_name'][i] == 'CD8a':
                                        cmap = 'red'
                                    elif df_indexed['Channel_name'][i] == 'Vimentin':
                                        cmap = 'yellow'
                                    else:
                                        cmap = 'gray'

                                    for tag in page.tags:
                                        tag_name, tag_value = tag.name, tag.value

                                    image = page.asarray()

                                    if 'Cycle' in df.columns and 'Fluorochrome' in df.columns:
                                        if df_indexed['Fluorochrome'][i] == '' :
                                            fullname = df_indexed['Cycle'][i] + ' ' + channel_name
                                        else:
                                            fullname = df_indexed['Cycle'][i] + ' ' + channel_name + ' (' + str(df_indexed['Fluorochrome'][i]) + ')'
                                    else:
                                        fullname = channel_name
                                        
                                    viewer.add_image(image, name = fullname, colormap=cmap, visible=False, blending='additive')
                                    i = i + 1

                        else: 
                            wrongtable = QMessageBox()
                            wrongtable.setText('The given table does not contain column Channel_numer and/or Antibody.\nPlease check your table, and edit it if necessary.')
                            wrongtable.exec()

                    else:
                        wrongformat = QMessageBox()
                        wrongformat.setText('File format is not supported,\nplease choose a .xlsx file!')
                        wrongformat.exec()

                else:
                    wrongpic = QMessageBox()
                    wrongpic.setText('File format is not supported,\nplease choose a .tif or .tiff file!')
                    wrongpic.exec()

                return core_name, channel_name_table, df_name
            
            gui = corepicker.Gui(show=True)
            viewer.window.add_dock_widget(gui, area='right')
            
        button = QPushButton("Multipage tif image loader")
        button.clicked.connect(open_corepicker)   

        def open_maskpicker():
            @magicgui(call_button='Get Masks', layout='vertical')
            def maskpicker(wholecount_mask_name=Path(),tablename=Path()):
                global img,mask_name,df_core_cellid,celltypes
                tname = str(tablename)

                if wholecount_mask_name.suffix == '.tif' or wholecount_mask_name.suffix == '.tiff':
                    img = tifffile.imread(wholecount_mask_name)
                    mask_name = Path(wholecount_mask_name).stem

                    if tname == '.':
                        viewer.add_labels(img, name=mask_name, num_colors=2)


                    elif tablename.suffix == '.csv':
                        df_data = pd.read_csv(tname)

                        if 'Core_Names' in df_data.columns and 'Cellid' in df_data.columns and 'GlobalCellType' in df_data.columns:       
                            viewer.add_labels(img, name=mask_name, visible = False, num_colors=2)
                            df_core = df_data[df_data.Core_Names == mask_name]
                            df_core_cellid = df_core.set_index('Cellid')
                            celltypes = df_core_cellid["GlobalCellType"].unique()
                            #color = {1: 'green', 2: 'orange', 3: 'purple', 4: 'papayawhip', 5: 'sienna'}

                            rows = img.shape[0]
                            cols = img.shape[1]
                            c = 1
                            global colorlist
                            colorlist = []

                            for l in range(len(celltypes)):
                                CelltypeMask = np.zeros(shape=(rows,cols),dtype=np.uint16)

                                for i in range(0,rows):
                                    for j in range(0,cols):
                                        id = img[i,j]
                                        if id in df_core_cellid.index and df_core_cellid['GlobalCellType'][id] == celltypes[l]:
                                            CelltypeMask[i,j] = c  
                                viewer.add_labels(CelltypeMask, name=celltypes[l] + '_Mask_' + mask_name, visible = False)
                                colorlist.append(viewer.active_layer.get_color(c))
                                c = c + 1
                                
                        else:
                            wrongtable2 = QMessageBox()
                            wrongtable2.setText('The given table does not contain column Cellid and/or Core_Names and/or GlobalCellType. Please check your table, and edit it if necessary.\nIf you have no correspontding table and only want to load a mask,\nplease leave the tablename slot empty.')
                            wrongtable2.exec()

                    else:
                        wrongformat2 = QMessageBox()
                        wrongformat2.setText('File format is not supported,\nplease choose a .csv file!')
                        wrongformat2.exec()

                else:
                    wrongpic2 = QMessageBox()
                    wrongpic2.setText('File format is not supported,\nplease choose a .tif or .tiff file!')
                    wrongpic2.exec()

                return img, df_core_cellid, mask_name, celltypes


            def area_plot():

                rows2 = img.shape[0]
                cols2 = img.shape[1]
                celltype_ids = []
                shape = viewer.layers[mask_name].data.shape
                selected_area = viewer.layers['Shapes'].to_labels(labels_shape=shape)
                viewer.add_labels(selected_area)

                for k in range(0,rows2):
                    for m in range(0,cols2):
                        id = img[k,m]
                        if img[k,m] > 0  and selected_area[k,m] == 1 and (id not in celltype_ids):
                            celltype_ids.append(id)

                celltypelist = celltypes.tolist()
                counter = np.zeros(len(celltypes))
                b = 0
                for n in range(len(celltype_ids)):
                    if celltype_ids[n] in df_core_cellid.index:
                        b = b + 1
                        a = celltypelist.index(df_core_cellid["GlobalCellType"][celltype_ids[n]])
                        counter[a] = counter[a] + 1

                values = counter/b*100
                print(counter)
                print(b)
                print(celltypelist)

                mpl_widget = FigureCanvas(Figure(figsize=(4, 6)))
                static_ax = mpl_widget.figure.subplots()
                colors=colorlist
                static_ax.set_xlabel('Celltypes', fontweight='demibold')
                static_ax.set_ylabel('Percentage in selected mask area', fontweight='demibold')
                static_ax.bar(celltypes,values, color=colors, width = 0.2)
                mpl_widget.show()

            plot_button = QPushButton("Get area plot")
            plot_button.clicked.connect(area_plot)
            
            gui2 = [maskpicker.Gui(show=True),plot_button]
            viewer.window.add_dock_widget(gui2, area='right')
            
        button2 = QPushButton("Celltype mask and percentage plot")
        button2.clicked.connect(open_maskpicker)  


        def open_markermask():
            class Marker(enum.Enum):
                Rabbit_488 = 'rabbit_488'
                Rat_555 = 'Rat_555'
                Mouse_647 = 'Mouse_647'
                CD11c = 'CD11c'
                BP53_1 = 'BP53_1'
                CD1c = 'CD1c'
                CD4 = 'CD4'
                CD3d = 'CD3d'
                CD20 = 'CD20'
                CD163 = 'CD163'
                CD57 = 'CD57'
                CD8a = 'CD8a'
                cCasp3 = 'cCasp3'
                pSTAT1 = 'pSTAT1'
                yH2AX = 'yH2AX'
                CD15 = 'CD15'
                Ki67 = 'Ki67'
                PDL1 = 'PDL1'
                IBA1 = 'IBA1'
                FOXP3 = 'FOXP3'
                PD1 = 'PD1'
                Ecadherin = 'Ecadherin'
                Vimentin = 'vimentin'
                CD31 = 'CD31'
                P21 = 'P21'
                CK7 = 'CK7'
                CD45 = 'CD45'

            @magicgui(call_button='Get Marker Intensity Mask', layout='vertical')
            def choosemarker(marker: Marker, mask=Path(), marker_intensity_table=Path()):
                table_name = str(marker_intensity_table)
                whole_mask_name = Path(mask).stem

                df = pd.read_csv(table_name)
                df_core = df[df.Core_Names == whole_mask_name]
                df_core_cellid = df_core.set_index('Cellid')

                whole_mask = imread(mask)

                MarkerMask = np.zeros(shape=whole_mask.shape,dtype=np.float64)

                rows = whole_mask.shape[0]
                cols = whole_mask.shape[1]

                for i in range(0,rows):
                    for j in range(0,cols):
                        id = whole_mask[i,j]
                        if id in df_core_cellid.index:
                            MarkerMask[i,j] = df_core_cellid[marker.value][id]

                viewer.add_image(MarkerMask, name=(marker.value + '_intensity') ,colormap='fire')
                
            gui3 = choosemarker.Gui(show=True)
            viewer.window.add_dock_widget(gui3, area='right')
            
        button3 = QPushButton("Marker intensity mask loader")
        button3.clicked.connect(open_markermask) 

        def open_channelfolder():
            @magicgui(call_button = 'Get Channels', channel_folder_name={'mode':'d'}, layout='vertical')
            def channel_folder_picker(channel_folder_name=Path(), channel_table_name=Path()):
                filelist = []
                filelist = list(channel_folder_name.glob('**/*'))
                df_name = str(channel_table_name)

                if df_name == '.':
                    notable = QMessageBox()
                    notable.setText('No table given, please choose an exisiting table with .xlsx format!')
                    notable.exec()

                elif channel_table_name.suffix == '.xlsx':
                    df = pd.read_excel(df_name)

                    if 'Channel_number' in df.columns and 'Channel_name' in df.columns:
                        df_indexed = df.set_index('Channel_number')
                        times = []

                        for i in range(len(filelist)):
                            thistime = os.path.getctime(filelist[i])
                            times.append(thistime)

                        times.sort()  
                        for l in range(len(times)):
                            ch_name = df_indexed['Channel_name'][l]
                            if df_indexed.index[l] % 4 == 0:
                                cmap = 'blue'
                            elif df_indexed['Channel_name'][l] == 'E-cadherin' or df_indexed['Channel_name'][l] == 'Ecadherin':
                                cmap = 'magenta'
                            elif df_indexed['Channel_name'][l] == 'CD4':
                                cmap = 'cyan'
                            elif df_indexed['Channel_name'][l] == 'CD8a':
                                cmap = 'red'
                            elif df_indexed['Channel_name'][l] == 'Vimentin':
                                cmap = 'yellow'
                            else:
                                cmap = 'gray'

                            for j in range(len(filelist)):
                                if times[l] == os.path.getctime(filelist[j]):
                                    print(filelist[j])
                                    stack = daskread(str(filelist[j]))
                                    viewer.add_image(stack, contrast_limits=[0,65535], multiscale=False, name=ch_name, colormap=cmap, visible=False, blending='additive')
                    else:
                        nocolumn = QMessageBox()
                        nocolumn.setText('The table does not contain the reqired Channel_number and/or Channel_name columns. Please edit the table, or choose another one!')
                        nocolumn.exec()

                else:
                    wrongformat = QMessageBox()
                    wrongformat.setText('The choosen file is not supported, please choose a table with .xlsx format!')
                    wrongformat.exec() 

                return channel_table_name, channel_folder_name

            gui4 = channel_folder_picker.Gui(show=True)
            viewer.window.add_dock_widget(gui4, area='right')
            
        button4 = QPushButton("Load multiple tif from folder")
        button4.clicked.connect(open_channelfolder) 

        def open_dna():
            @magicgui(call_button = 'Get DNA Channels', channel_folder_for_DNA={'mode':'d'}, layout='vertical')
            def channel_folder_picker2(channel_folder_for_DNA=Path(), channel_table_for_DNA=Path()):
                filelist = []
                filelist = list(channel_folder_for_DNA.glob('**/*'))
                df_name = str(channel_table_for_DNA)

                if df_name == '.':
                    notable = QMessageBox()
                    notable.setText('No table given, please choose an exisiting table with .xlsx format!')
                    notable.exec()

                elif channel_table_for_DNA.suffix == '.xlsx':
                    df = pd.read_excel(df_name)

                    if 'Channel_number' in df.columns and 'Channel_name' in df.columns:
                        df_indexed = df.set_index('Channel_number')
                        times = []

                        for i in range(len(filelist)):
                            thistime = os.path.getctime(filelist[i])
                            times.append(thistime)

                        times.sort()  
                        for l in range(len(times)):
                            ch_name = df_indexed['Channel_name'][l]
                            if df_indexed.index[l] % 4 == 0:
                                cmap = 'blue'
                                for j in range(len(filelist)):
                                    if times[l] == os.path.getctime(filelist[j]):
                                        print(filelist[j])
                                        stack = daskread(str(filelist[j]))
                                        viewer.add_image(stack, contrast_limits=[0,65535], multiscale=False, name=ch_name, colormap=cmap, blending='additive')
                    else:
                        nocolumn = QMessageBox()
                        nocolumn.setText('The table does not contain the reqired Channel_number and/or Channel_name columns. Please edit the table, or choose another one!')
                        nocolumn.exec()

                else:
                    wrongformat = QMessageBox()
                    wrongformat.setText('The choosen file is not supported, please choose a table with .xlsx format!')
                    wrongformat.exec() 

                return channel_table_for_DNA, channel_folder_for_DNA
            
            gui5 = channel_folder_picker2.Gui(show=True)
            viewer.window.add_dock_widget(gui5, area='right')
            
        button5 = QPushButton("Load DNA channels from folder")
        button5.clicked.connect(open_dna) 

        def open_maskfolder():
            @magicgui(call_button = 'Get Masks as image', mask_folder={'mode':'d'}, layout='vertical')
            def mask_folder_picker(mask_folder=Path()):
                masklist = []
                masklist = list(mask_folder.glob('**/*'))

                for n in range(len(masklist)):
                    mask_name = Path(masklist[n]).stem
                    mask = daskread(str(masklist[n]))
                    viewer.add_image(mask, contrast_limits=[0,65535], multiscale=False, name = mask_name, blending='additive')
                    
            gui6 = mask_folder_picker.Gui(show=True)
            viewer.window.add_dock_widget(gui6, area='right')
            
        button6 = QPushButton("Load masks as image from folder")
        button6.clicked.connect(open_maskfolder) 

        def open_maskfolder2():
            @magicgui(call_button = 'Get Masks as labels', mask_folder_for_labels={'mode':'d'}, layout='vertical')
            def mask_folder_picker2(mask_folder_for_labels=Path()):
                masklist2 = []
                masklist2 = list(mask_folder_for_labels.glob('**/*'))

                for n in range(len(masklist2)):
                    mask_name2 = Path(masklist2[n]).stem
                    mask2 = tifffile.imread(masklist2[n])
                    viewer.add_labels(mask2, name = mask_name2, num_colors=2, blending='additive')

            gui7 = mask_folder_picker2.Gui(show=True)
            viewer.window.add_dock_widget(gui7, area='right')
            
        button7 = QPushButton("Load masks as label from folder")
        button7.clicked.connect(open_maskfolder2) 

        def delete_all_layers():
                viewer.layers.select_all()
                viewer.layers.remove_selected()        
                
        clear_button = QPushButton("Delete all displayed layers")
        clear_button.clicked.connect(delete_all_layers)

        buttongui = [button, button2, button3,button4,button5, button6, button7]
        viewer.window.add_dock_widget(buttongui, area='right')

        viewer.window.add_dock_widget(clear_button, area='left')





