To run use terminal / command line and write
`Rscript .\produce_report.R [path1] [path2-optional]`

e.g. `Rcript .\produce_report.R "C:\data\iteration1" "C:\data\iteration2"`

If two paths are provided, the report will contain comparison plots.


### Update of the qc_functions2.R script


Inside your script for calling cell types source the `qc_functions2.R` script, make sure you installed before all packages imported in the first lines. 
The most informative plot are the:
1. `channel.densities()`
2. `index_plots()`
3. `channel.UMAPs()`

Examples of use (this need better explanations):

#### channel.UMAPs() example:

For these examples, the object "df\_merged\_global" is a data.frame corresponding to the table if cell intensities and at the last column the celltypes, last column should be named GlobalCellType. I merged the ImmuneCelltype and GlobalCellType columns using the function `combine_gates()`.

```
	immune.interesting.channels <- unique(unlist(c(Myeloid.gate, immune.gates, Lymphoid.gate)))
        immune.data <- df_merged_global[df_merged_global$GlobalCellType != "Cancer" ,immune.interesting.channels]
        immune.types <- df_merged_global[df_merged_global$GlobalCellType != "Cancer" ,"GlobalCellType"]
        
        #cell_type <- factor(Immune.Types, levels=(unique(Immune.Types))) #Cell type for each row
        cell_type <- factor(immune.types, levels=(unique(immune.types))) #Cell type for each row
        umaps.plots <- channel.UMAPs(immune.data, cell_type, sub.sample = TRUE, n.sampling = nrow(immune.data))
	ggsave(file=paste0(outout.folder.name,"Immune_UMAPs_channels_untruncated.pdf"), arrangeGrob(grobs = umaps.plots[[1]], ncol = 4), height = 14, width = 16)
        ggsave(file=paste0(outout.folder.name,"Immune_UMAPs_channels_untruncated.png"), arrangeGrob(grobs = umaps.plots[[1]], ncol = 4), height = 5.3, width = 6.1)
        ggsave(file=paste0(outout.folder.name,"Immune_UMAPs_celltypes_untruncated.pdf"), umaps.plots[[2]], height = 6.89, width = 7.93)
```
#### channel.densities()

```
        densities.by.channels <- channel.densities(immune.data)
	ggsave(file=paste0(outout.folder.name,"Immune_channel_densities.pdf"), arrangeGrob(grobs = densities.by.channels, ncol = 4), height = 14, width = 16)
        ggsave(file=paste0(outout.folder.name,"Immune_channel_densities.png"), arrangeGrob(grobs = densities.by.channels, ncol = 4), height = 6.89, width = 7.93)
```

#### index_plots()

```
	pdf(file= paste0(outout.folder.name,"Total_celltypes_markerExpression.pdf"), height = 8, width = 10)
        ind.plots = index_plots(df_merged_global,df_merged_global, gates.input=c(global.gates, immune.gates, Lymphoid.gate, Myeloid.gate), scaling = "z.score")
        print(ind.plots[[3]])
        dev.off()
```
