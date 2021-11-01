# Cell type caller edited from Topacio dataset.
# Structure:
## 1 import libraries and data
## 2 Load cellTypeCaller function
## 3 Hopefully enjoy bug-free execution
#
# Select each block of code and press Ctrl+Enter to run
#

library(corrplot)
library(reshape2)
library(ggplot2)

library(flowCore)
library(FlowSOM)
# For these you need Biocmanager if not installed
if (!requireNamespace("BiocManager", quietly = TRUE))
  install.packages("BiocManager")

BiocManager::install("FlowSOM")

library(sjstats)
library(BBmisc)
library(matrixStats)
library(pheatmap)
library(RColorBrewer)
library(dplyr)
library(foreach)
library(doParallel)
library(uwot)

library(future.apply)
library(doFuture)

# Set at least the current iteration to something that describes your run
iteration = '4non_noothers'
old.iteration = '4gate'

# Edit these to correspond to the naming of your dna and background channels
# E.g my DNA channels were Hoechst_1 etc. so a regexp to catch that is Hoech
# Separate bg channels with a pipe. Here's a couple extras in case you need them ||||||||||||||||||||||||||
dnachannel = 'Hoech'
bgchannels = 'Mouse|Rabbit|Goat'

## Set the directory to your working directory that contains the output data from QC
setwd("D:/Analysis")
dir.create("plots", showWarnings = FALSE)
dir.create("gated", showWarnings = FALSE)


# List all the data
files <- list.files(paste0(getwd(),"/filtered_data"), full.names = T)
files <- files[grepl(pattern = "filtered", x=files)]
# Hopefully you don't have to edit this regex
names(files) <- gsub('[.].*','',gsub('filtered_','',gsub(".*/(.*).*", "\\1", files)))
registerDoFuture()
plan(multiprocess)
# Adjust this to reflext the max space needed for your data
options(future.globals.maxSize= 5*1024^3)
data <- future_lapply(files, read.csv, sep=',', stringsAsFactors = F)
names(data) <- names(files)

# If the data loading above took a significant amount of time, it might be worthwhile to save the data to a faster format
# In that case, uncomment the following line
# save(data, file='data_ring.Rdata')
# then, you can skip the 'List all the data' block by running the load command that is MUCH faster than reading a bunch of csv files
# load('data.Rdata')



##############################
##  Gate calls
##  The block is wrapped in curly brackets to make sure all the required steps are run
##############################
{
mydata <- data

## If data is not log normalized
mydata <- lapply(mydata, log10)
for(sample.name in names(mydata)) {
  cols <- which(colnames(mydata[[sample.name]])=='Area'):ncol(mydata[[sample.name]])
  mydata[[sample.name]][,cols] = data[[sample.name]][,cols] 
}


labeled <- list()
# Edit this based on your sample names. My samples were named 'Sample_1', 'Sample_2' etc.
samples <- grep("Sample",names(mydata), value=TRUE)
cell.counts <- list()

#cores=detectCores()
#cl <- makeCluster(cores[1]-1) #adjust the amount of cores based on the sample's size. Whole tissue slides overload the RAM on 64 GB machine with more than 2 cores
#cl <- makeCluster(6)
#registerDoParallel(cl)

comb <- function(x, ...) {  
  c(...)
}
# Make sure that the directory also has the celltypecaller function in this external file
source('2b_cell_type_caller.R')
source('qc_funcs.R')
# Load the external gates.R file that contains cell type gatings
source('gates.R')

for(sample.name in samples) {
  folder.name <- paste0("plots/", sample.name,"_gating")
  dir.create(folder.name, showWarnings = FALSE)
}

# Run the celltypecaller in parallel. No prints are made when running this way
labeled <- foreach(sample.name=samples, .combine = 'comb', .multicombine = T, .init=list(data.frame()), .packages = c('corrplot','reshape2','ggplot2','flowCore','FlowSOM','sjstats','BBmisc','matrixStats','pheatmap','RColorBrewer','dplyr')) %dopar% { #[grep('19', samples)]
  cat("Starting",sample.name,"...\n")
  t0 <- Sys.time()
  folder.name <- paste0("plots/", sample.name,"_gating")
  # First call global cell types
  globalTypes <- cellTypeCaller(mydata[[sample.name]], global.gates, "GlobalCellType", folder.name = folder.name)
  firstGate <- merge(x=mydata[[sample.name]], y=globalTypes, all.x=T, by="CellId")
  
  
  idx <- grep('Stromal', firstGate$GlobalCellType)
  firstGate$GlobalCellType[idx] <- "Stromal.cells"
  
  idx <- grep('Other', firstGate$GlobalCellType)
  firstGate$GlobalCellType[idx] <- "Other"
  
  # Then call subtypes of immune cells
  idx <- grep('Immune', firstGate$GlobalCellType)
  firstGate$GlobalCellType[idx] <- "Immune.cells"
  
  idx <- grep('Tumor', firstGate$GlobalCellType)
  firstGate$GlobalCellType[idx] <- "Tumor.cells"
  print(table(firstGate$GlobalCellType))
  
  sub.df <- firstGate[which(firstGate$GlobalCellType == "Immune.cells"),]
  if(nrow(sub.df)<100) {
    cat("cellType label has less than 100 immune cells.\n")
    next
  }else {
    cat(nrow(sub.df), "Immune cells passed to next gate.\n")
  }
  # Segond gate
  immuneTypes <- cellTypeCaller(sub.df, immune.gates, "ImmuneCellType", folder.name = folder.name)
  secondGate <- merge(x=firstGate, y=immuneTypes, all.x=T, by="CellId")
  print(table(immuneTypes$ImmuneCellType))
  
  sub.df <- secondGate[which(secondGate$ImmuneCellType == "CD8.T.cells"),]
  if(nrow(sub.df)<100) {
    cat("ImmuneCellType label has less than 100 CD8+ cells.\n")
    thirdGate <- secondGate
  }else {
    cat(nrow(sub.df), "CD8+ cells passed to next gate.\n")
    # Third gate
    cd8Types <- cellTypeCaller(sub.df, cd8.gates, "CD8TCellType", folder.name = folder.name)
    thirdGate <- merge(x=secondGate, y=cd8Types, all.x=T, by="CellId")
    print(table(cd8Types$CD8TCellType))
  }
  
  sub.df <- secondGate[which(secondGate$ImmuneCellType == "Macrophages"),]
  if(nrow(sub.df)<100) {
    cat("ImmuneCellType label has less than 100 Macrophages.\n")
    fourthGate <- thirdGate
  }else {
    cat(nrow(sub.df), "Macrophages passed to next gate.\n")
    # Third gate
    macsTypes <- cellTypeCaller(sub.df, macrophage.gates, "MacrophageType", folder.name = folder.name)
    fourthGate <- merge(x=thirdGate, y=macsTypes, all.x=T, by="CellId")
    print(table(macsTypes$MacrophageType))
  }
  
  sub.df <- secondGate[which(secondGate$ImmuneCellType == "CD4.T.cells"),]
  if(nrow(sub.df)<100) {
    cat("ImmuneCellType label has less than 100 CD4 T-cells\n")
    fifthGate <- fourthGate
  }else {
    cat(nrow(sub.df), "CD4 T-cells passed to next gate.\n")
    # Third gate
    cd4Types <- cellTypeCaller(sub.df, cd4.gates, "CD4Type", folder.name = folder.name)
    fifthGate <- merge(x=fourthGate, y=cd4Types, all.x=T, by="CellId")
    print(table(cd4Types$CD4Type))
  }
  
  sub.df <- secondGate[which(secondGate$ImmuneCellType == "Antigen.presenting.cells"),]
  if(nrow(sub.df)<100) {
    cat("ImmuneCellType label has less than 100 Antigen presenting cells\n")
    sixthGate <- fifthGate
  }else {
    cat(nrow(sub.df), "APC-cells passed to next gate.\n")
    # Third gate
    apcTypes <- cellTypeCaller(sub.df, dc.gates, "APCType", folder.name = folder.name)
    sixthGate <- merge(x=fifthGate, y=apcTypes, all.x=T, by="CellId")
    print(table(apcTypes$APCType))
  }
  
  sub.df <- secondGate[which(secondGate$GlobalCellType == "Stromal.cells"),]
  if(nrow(sub.df)<100) {
    cat("CellType label has less than 100 stromal cells\n")
    seventhGate <- sixthGate
  }else {
    cat(nrow(sub.df), "stromal cells passed to next gate.\n")
    # Third gate
    stromaTypes <- cellTypeCaller(sub.df, stroma.gates, "STROMAType", folder.name = folder.name)
    seventhGate <- merge(x=sixthGate, y=stromaTypes, all.x=T, by="CellId")
    print(table(stromaTypes$STROMAType))
  }
  
  # Looking for possible langerhans cells
  #sub.df <- secondGate[which(secondGate$GlobalCellType == "Tumor.cells"),]
  #if(nrow(sub.df)<100) {
  #  cat("CellType label has less than 100 tumor cells\n")
  #  eighthGate <- seventhGate
  #}else {
  #  cat(nrow(sub.df), "tumor cells passed to next gate.\n")
  #  # Third gate
  #  tumorTypes <- cellTypeCaller(sub.df, tumor.gates, "tumorType", folder.name = folder.name)
  #  eighthGate <- merge(x=seventhGate, y=tumorTypes, all.x=T, by="CellId")
  #  print(table(tumorTypes$tumorType))
  #}
  
  #print(table(seventhGate$ImmuneCellType)/sum(table(seventhGate$ImmuneCellType)))
  
  #labeled[[sample.name]] <- seventhGate
  
  #lastGate = seventhGate
  
  #print.xy.plot(seventhGate, sample.name)
  #print.xy.plot(seventhGate, sample.name,F)
  # Save cellType column
  # Uncomment the next line if you'd like to get the output data. I have it commented as it slows the iteration process down
  # write.table(seventhGate, paste0("gated/new_",sample.name,"_gated.csv"), row.names = F)
  eltim = Sys.time() - t0
  cat('Elapsed time',eltim,units(eltim),'\n')
  tryCatch({dev.off()},error=function(cond){return(NA)})
  
  seventhGate$sample=rep(sample.name)
  endresult = list()
  endresult[[sample.name]] = seventhGate
  return(endresult)
}
#stopCluster(cl)

}
save(labeled, file=paste0('labeled_ring_',iteration,'.Rdata'))
# If that took a while, you could save the data again in a nice format by uncommenting the next line
# save(labeled, file=paste0('labeled_ring_',iteration,'.Rdata'))
####################
### END OF CELL TYPE CALLING
########


for(sample.name in names(labeled)) {
  seventhGate = labeled[[sample.name]]
  print.xy.plot(seventhGate, sample.name)
  print.xy.plot(seventhGate, sample.name,F)
}


for(sample.name in names(labeled)) {
  labeled[[sample.name]] = labeled[[sample.name]][labeled[[sample.name]]$GlobalCellType!='Other',]
  labeled[[sample.name]] = labeled[[sample.name]][!labeled[[sample.name]]$ImmuneCellType%in%c('Other'),]
}

### Summary plots after caller



# The first pie chart and the for loop after it plots each sample to it's own file.

#for(sample.name in names(labeled)) plot_pie_charts(labeled, sample.name)
plot_pie_charts2(labeled)
plot_heatmaps(labeled)
plot_qc_plot(labeled.old,labeled)
plot_umaps(labeled)

