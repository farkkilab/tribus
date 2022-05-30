## This file contains several helper functions used in the production of the final report
## created based on an old R implementation of Tribus cell type caller. Naming conventions etc. might have changed
## At least the format of gates is changed and needs to be updated when I get an example of the new format
## TODO check if data needs to be scaled between samples or if it already is

library(viridis)
library(ggplot2)
library(tidyverse)
library(uwot)
library(RcppParallel)
library(reshape2)
library(ggalluvial)
library(caTools)
library(ComplexHeatmap)
options(dplyr.summarise.inform = FALSE)
library(BBmisc)

#TODO: These should be figured out automatically once we switch to the new gate format

# Assigned cell type in the first iteration of the cell type caller. Stroma - Tumor - Immune
GlobalCellType = "GlobalCellType"

cell.type.column = "GlobalCellType"

# Assigned immune cell identities. E.g. T/B cells, macrophages etc.
ImmuneCellType = "ImmuneCellType"

# The name of the DNA channel in the dataset
dnachannel = 'DNA'
# Names of the background channels separated with pipes
bgchannels = 'Mouse|Rabbit|Goat'

#TODO: Update this to fit the change of list -> df
# Plot a pie chart of the cell type composition of the whole dataset
pie_charts = function(samplelist) {
  data.temp = data.frame()
  for(sn in names(samplelist)) {
    data.temp = rbind(data.temp,data.frame(cell.type=samplelist[[sn]][,cell.type.column]))
  }
  p = ggplot(data = subset(data.temp,!is.na(cell.type)), aes(x=factor(1), fill=cell.type)) + geom_bar(width=1) + coord_polar('y',start=0) 
  p = p + ggtitle(paste0('Composition of the dataset')) + ylab('Cell types') + xlab('') + scale_fill_brewer(palette="Paired")
  p = p + theme(legend.position='bottom', legend.text = element_text(size=8))
  return(p)

}


# Procuces pie charts of the cell type compositions in the data faceted by samples
all_pie_charts = function(piedf, group.by="sample") {
  data.temp = piedf %>% 
    group_by(eval(parse(text=group.by)), GlobalCellType) %>% 
    summarise(n = n()) %>% 
    mutate(perc = n / sum(n))
  colnames(data.temp)[1] <- "group"
  
  p = ggplot(data.temp, aes(x=factor(1), y=perc, fill=GlobalCellType)) + geom_bar(stat='identity',width=1) + coord_polar('y',start=0) 
  p = p + ggtitle(paste0('Composition of samples')) + ylab('Cell types') + xlab('') + scale_fill_brewer(palette="Paired") 
  p = p + facet_wrap(~group, ncol = 8) + theme(legend.position='bottom', legend.text = element_text(size=8))
  return(p)
}

# Produces bar charts visualizing the changes in different cell types in the samples
compare_compositions = function(new, old) {
  stopifnot("The two iterations should have the same samples" = unique(old$sample) == unique(new$sample))
  tmp = df.old %>% group_by(sample, GlobalCellType) %>% summarise(n_old = n(), n_new=0)
  tmp2 = df.new %>% group_by(sample, GlobalCellType) %>% summarise(n_new = n(), n_old=0)
  
  data.temp = rbind(tmp,tmp2) %>% group_by(sample, GlobalCellType) %>% mutate(n = sum(n_old)-sum(n_new))
  data.temp = data.temp[1:nrow(tmp),]
  tot_chg = data.temp %>% group_by(GlobalCellType) %>% summarise(tot=sum(n))
  #p = ggplot(data.temp, aes(x=cell.name,y=change, fill=cell.name)) + geom_bar(stat='identity') + facet_wrap(~sample, ncol = 8)+ theme(legend.position='bottom', legend.text = element_text(size=8),axis.text.x = element_blank(), axis.ticks = element_blank(), legend.title = element_blank()) + xlab('')
  p_whole = ggplot(tot_chg, aes(x=GlobalCellType,y=tot, fill=GlobalCellType)) + geom_bar(stat='identity') + theme(legend.position='bottom', legend.text = element_text(size=8),axis.text.x = element_blank(), axis.ticks = element_blank(), legend.title = element_blank()) + xlab('') + geom_hline(yintercept = 0)
  p = ggplot(data.temp, aes(x=GlobalCellType,y=n, fill=GlobalCellType)) + geom_bar(stat='identity') + theme(legend.position='bottom', legend.text = element_text(size=8),axis.text.x = element_blank(), axis.ticks = element_blank(), legend.title = element_blank()) + xlab('') + geom_hline(yintercept = 0) + facet_wrap(~sample, ncol = 8)
  return(list(p,p_whole))
}

# Plots XY plot with either the global cell types or global + immune subtypes
# TODO check that it works if needed
# Currently unchecked old implementation as previously it was discussed that XY plotting could be done
# in Napari?
xy_plot <- function(df, sample.name, extendImmunes =T){ 
  df[,cell.type.column] <- df[GlobalCellType]
  if(extendImmunes) df[,cell.type.column][which(df[GlobalCellType]=="Immune.cells")] <- df[ImmuneCellType][which(df[GlobalCellType]=="Immune.cells")]
  # TODO check this
  df[,cell.type.column][ which(df[,cell.type.column] %in% c("Other2","Other","Unknown"))] <- "Other" #NA
  ntypes <- length(unique(df[,cell.type.column]))
  mycolors <- colorRampPalette(brewer.pal(8, "Set2"))(ntypes)
  
  p <- ggplot(df, aes(x=X_position, y=Y_position, color=cell.type)) + geom_point(size=1, stroke=0, shape='.') + scale_color_manual(values=mycolors, na.value = "grey50") + theme_bw() + ggtitle(sample.name) + coord_fixed(ratio = 1) + scale_y_reverse() + guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
  return(p)
  #gname <- paste0("XY_", sample.name, "scatter_by_",ifelse(!base.or.immune,'global','immune'),"CellType_",iteration,".pdf")
  #ggsave(plot=p, filename = gname, device="pdf")
}


# TODO this can be made computationally more efficient, if combined with compare compositions etc as they loop over all the samples
# For the gates it can be used several of them in combination, example: gates=c(global.gates,immune.gates)
#Options for scaling = z.score, mad, min.max, none
index_plots = function(new, old, gates.input=global.gates, scaling="z.score") {
  # Firstly combine the sample data to a single data frame containing only columns of interest
  # TODO in the current version of cell type caller, the result might already be in a single df making this step redundant
  ###
  
  
  cols_to_keep = marker.in.gates(colnames(new), gates.to.use=gates.input)
  #cols_to_keep[c(1,which(colnames(new)==GlobalCellType))] = T
  cols_to_keep[which(colnames(new)==GlobalCellType)] = T
  df.new = new[,cols_to_keep]
  
  cols_to_keep = marker.in.gates(colnames(old), gates.to.use=gates.input)
  #cols_to_keep[c(1,which(colnames(new)==GlobalCellType))] = T
  cols_to_keep[which(colnames(new)==GlobalCellType)] = T
  df.old = old[,cols_to_keep]
  
  #scaling data
  if (scaling == "z.score"){
      df.new[,-ncol(df.new)] = BBmisc::normalize(scale(df.new[,-ncol(df.new)]), method='range')
      df.old[,-ncol(df.old)] = BBmisc::normalize(scale(df.old[,-ncol(df.old)]), method='range') #scaling data
  } else if (scaling == "mad"){
      mads.new <- sapply(df.new[,-ncol(df.new)], mad)
      mads.old <- sapply(df.new[,-ncol(df.new)], mad)
      for (i in 1:ncol(df.new[,-ncol(df.new)])){
        df.new[,i] = (df.new[,i] - median(df.new[,i])) / mads.new[i]
        df.old[,i] = (df.old[,i] - median(df.old[,i])) / mads.old[i]
      }
  } else if (scaling == "min.max"){
    df.new[,-ncol(df.new)] <- sapply(df.new[,-ncol(df.new)], min_max_norm)
    df.old[,-ncol(df.old)] <- sapply(df.old[,-ncol(df.old)], min_max_norm)
  } else if (scaling == "robust"){
    df.new[,-ncol(df.new)] <- sapply(df.new[,-ncol(df.new)],   robust_scalar)
    df.old[,-ncol(df.old)] <- sapply(df.old[,-ncol(df.old)],   robust_scalar)
  } else{
    print(paste0("No normalization performed in input data"))
  }
  
  appeared.or.disappeared.types = c(setdiff(unique(df.new[,GlobalCellType]),unique(df.old[,GlobalCellType])),
                                    setdiff(unique(df.old[,GlobalCellType]),unique(df.new[,GlobalCellType])))
  
  data.temp = bind_rows(df.old,df.new, .id = "iter") %>%  mutate(iter=if_else(iter == 1, "old", "new"))
  ###
  
  # Marker index
  means.by.cell.type = data.temp %>% group_by(GlobalCellType,iter) %>% summarise(across(where(is.numeric),.fns = median))#[1:(ncol(data.temp)-3)],.funs = mean)
  sds.by.cell.type = data.temp %>% group_by(GlobalCellType,iter) %>% summarise(across(where(is.numeric),.fns = sd))
  plot.data = melt(means.by.cell.type, id.vars = c(cell.type.column,'iter')) #Value column is the mean
  plot.data$pairs = NA
  ind = !(plot.data[,cell.type.column] %in% appeared.or.disappeared.types)
  plot.data$pairs[ind] = rep(1:(sum(ind)/2),each=2)
  linecol = subset(plot.data[ind,],!is.na(plot.data[ind,][,cell.type.column])) %>% group_by(pairs) %>%summarise_at(.vars="value",.funs = function(x){ifelse(sum(x*c(1,-1))>0,'new','old')})
  linecol = rep(linecol$value, each=2)
  p = ggplot(data = plot.data, aes(x=variable,y=value,color=iter)) +
        geom_point() + facet_wrap(as.formula(paste0("~",cell.type.column))) +
        theme(axis.text.x = element_text(angle = 45, hjust = 1,size = 5)) +
        geom_line(data=subset(plot.data,!is.na(plot.data$pairs)),aes(group=pairs,color=linecol)) +
        geom_hline(yintercept=0.5, linetype="dashed", color = "brown", size=0.5)

  gi  = data.frame() #Calculating gate index and storing those in gi
  for(i in 1:nrow(means.by.cell.type)) {
    cell.type = unlist(means.by.cell.type[,cell.type.column])[i]
    if(cell.type %in% gsub(" ",".",names(gates.input))){
      gates = gates.input
    }else {
      print(paste0(cell.type, " not found in input gates"))
    }
    tmp.gates = unlist(gates[grep(cell.type,names(gates))])
    if(is.null(tmp.gates)) {
      warning(paste0('No gates for cell type ',cell.type))
      next
    }
    pos = unique(tmp.gates[grep('Pos', names(tmp.gates))])
    neg = unique(tmp.gates[grep('Neg', names(tmp.gates))])
    neg = neg[which(neg%in%colnames(means.by.cell.type))]
    pos = pos[which(pos%in%colnames(means.by.cell.type))]
    
    #make a backup
    meansct = means.by.cell.type
    means.by.cell.type[do.call(cbind,lapply(means.by.cell.type, is.infinite))] <- 0 #Replace infinities with 0 (not ideal)
    
    ##
    # TODO come up with a better statistic; probably scaling the input data
    # ver.1 sum of positive markers - sum of negative markers
    # ver.2 average of positive markers - average of negative markers
    ##
    if (length(neg)){ #Adding if for cell-types without negative markers
      gate.index = sum(means.by.cell.type[i,pos])/length(pos)-sum(means.by.cell.type[i,neg])/length(neg)
    }else{
      gate.index = sum(means.by.cell.type[i,pos])/length(pos)
    }
    
    means.by.cell.type = meansct
    gi = rbind(gi, data.frame(index=gate.index, cell.type=cell.type, iter = means.by.cell.type$iter[i]))
  }
  gi$pairs = rep(1:(nrow(gi)/2),each=2)
  linecol2 = gi %>% group_by(pairs) %>%summarise_at(.vars="index",.funs = function(x){ifelse(sum(x*c(1,-1))>0,'new','old')})
  linecol2 = rep(linecol2$index, each=2)
  pgi = ggplot(data = gi, aes(x=cell.type,y=index,color=iter)) + geom_point() + theme(axis.text.x = element_text(angle = 45, hjust = 1,size = 5)) + geom_line(aes(group=pairs,color=linecol2))
  plots = list(p,pgi)
  
  # Heatmaps
  for(fiter in c("new", "old")) {
    hmap.subset = data.frame(filter(means.by.cell.type,iter==fiter)[,-2])
    sd.subset = data.frame(filter(sds.by.cell.type,iter==fiter)[,-2])
    row.names(hmap.subset) = hmap.subset[,cell.type.column]
    row_ha = rowAnnotation(N.cells=anno_barplot(as.vector(table(pull(filter(data.temp,iter==fiter),cell.type.column)))))
    ph = plot.heatmap(hmap.subset[,-1],sd.subset[,-1],row_anno=row_ha)
    plots = append(plots,ph)
  }
  return(plots)
}

# TODO this
heatmap_plot = function(new, old){
  ## Heatmaps for each cell type in each sample
  data.tmp <- labeled
  # Apply the amount of cell types you want to be shown in the plot
  data.tmp <- lapply(data.tmp, combine.gates) # Tumor - Stroma - Immune
  #data.tmp <- lapply(data.tmp, detailed.gates) # Tumor - Immune subtypes - Stroma
  for(sample.name in names(data.tmp)){ 
    means.by.cell.type <- get_means(sample.name, data.tmp,functionals)
    plot.heatmap(means.by.cell.type, scalem = "column", title = sample.name, fname = paste0(sample.name, "_cell_type_means_",iteration,if(functionals)"_func" else "",".pdf"))
  }
}
plot.heatmap <- function(data, sds, scalem="none", title=NULL,colors=NULL, row_anno) {
  mat2 = as.matrix(data)
  return(Heatmap(mat2, column_title  = "Numerical values inside cells represents the standard deviation", column_title_side="bottom",
           column_title_gp = gpar(fontsize = 8), cluster_rows=T, border = T,name='Scale', width = ncol(mat2)*unit(7, "mm"), height = nrow(mat2)*unit(7, "mm"),
           color=colorRampPalette(c("#0e74b3","white","#cf242a"),interpolate="linear")(200), right_annotation=row_anno,
           column_names_rot = 45,row_names_gp = gpar(fontsize = 8),column_names_gp = gpar(fontsize = 8),heatmap_legend_param = list(direction = "horizontal"),
           cell_fun = function(j, i, x, y, width, height, fill) {
             grid.text(sprintf("%.2g", sds[i, j]), x, y, rot=45, gp = gpar(fontsize = 6))
           }))
}

# TODO match.row for possible changes in cell ordering?
plot_alluv <- function(new, old) {
  df.new = new[,c("sample","ID",cell.type.column)]
  df.old = old[,c("sample","ID",cell.type.column)]
  
  df.comb = bind_cols(df.old[,3],df.new[,3])
  colnames(df.comb) = c("Old cell type", "New cell type")
  df.comb = count(df.comb, `Old cell type`, `New cell type`) %>% ungroup()
  p = ggplot(df.comb, aes(y=n,axis1=`Old cell type`, axis2=`New cell type`)) + 
    geom_alluvium(aes(fill =`Old cell type`), width = 1/12) +geom_stratum(width = 1/12, fill="black", color="grey") + 
    geom_label(stat="stratum",aes(label=after_stat(stratum))) +
    scale_x_discrete(limits = c("Old cell type", "New cell type"), expand = c(.05,.05)) +
    scale_fill_brewer(type = "qual", palette = "Set1") +
    ggtitle("Changes in cell types") +
    theme(axis.text.y = element_blank(), panel.background = element_rect(fill = "white", colour = "grey50")) + ylab("")
  return(p)
}

#Function required for some plotting methods
#Merge cell-types labels from subsequent gates in the GlobalCellType column
#And cells with labels as other or Unknown, give then the unified name "Other"
combine_gates <- function(df, immune_labels=c("Immune.cells"), label_for_Others=c("Other2","Other","Unknown")) {
  df[,cell.type.column] <- df[,GlobalCellType]
  df[,cell.type.column][which(df[,GlobalCellType] %in% immune_labels)] <- df[,ImmuneCellType][which(df[,GlobalCellType] %in% immune_labels)]
  #TODO check if the label for others
  df[,cell.type.column][ which(df[,cell.type.column] %in% label_for_Others)] <- "Other"#NA
  return(df)
}

# This is used to load a RData object to a differently named variable
loadRData <- function(fileName){
  varnames = ls()
  #loads an RData file, and returns it
  load(fileName)
  get(ls()[!(ls() %in% varnames)])
}

# This function requires you to source the gates to memory and to have gates with the names global.gates and immune.gates
# TODO gate format has changed and this needs to be updated once I get the new format
# Here, functional marker is determined as a marker not used in gating
marker.in.gates = function(x, gates.to.use=global.gates,functionals=FALSE){
  included = x%in%unlist(gates.to.use)
  if(functionals) included = !included
  return(included)
}

plot.umaps = function(df, tit="Title"){
  # Area and eccentricity are kept
  df <- df.old
  gct = as.factor(df[,GlobalCellType])
  subsplit = ifelse(length(gct)<100000,length(gct),100000)
  subsplit = sample.split(gct,subsplit)
  df.umap = umap(df[subsplit,c(-(1:5),-ncol(df))], n_neighbors = 50, learning_rate = .5, y=gct)
  p = ggplotGrob(ggplot(df[subsplit,]) + geom_point(aes(x=df.umap[,1],y=df.umap[,2],col=GlobalCellType),size=0.2) + theme_void() + ggtitle(tit))
  p2 = ggplotGrob(ggplot(df[subsplit,]) + geom_point(aes(x=df.umap[,1],y=df.umap[,2],col=sample),size=0.2) + theme_void() + ggtitle(tit))
  grid::grid.newpage()
  grid::grid.draw(rbind(p, p2))
}


#Density plot for two channels at the same time
density.two.channels.by.class <- function(data, label="Cancer", channel1="CK7", channel2="ECadherin", label.column="Immune.Types"){
  df1 <- data[data[,label.column] != label,]
  df2 <- data[data[,label.column] == label,]
  
  p1 <- ggplot(df1, aes_string(x=channel1, y=channel2)) +
    stat_density_2d(aes(fill = ..level..), geom = "polygon") +
    scale_fill_continuous(type = "viridis") +
    ylim(min(data[,channel2]),max(data[,channel2])) +
    xlim(min(data[,channel1]),max(data[,channel1])) +
    theme(legend.position = "right")
  
  p2 <- ggplot(df2, aes_string(x=channel1, y=channel2)) +
    stat_density_2d(aes(fill = ..level..), geom = "polygon") +
    scale_fill_continuous(type = "viridis") +
    ylim(min(data[,channel2]),max(data[,channel2])) +
    xlim(min(data[,channel1]),max(data[,channel1])) +
    theme(legend.position = "right")
  fig <- ggarrange(p1, p2, labels = c(paste0("Non-",label), label), ncol = 2, nrow = 1)
  return(fig)
}


#####UMAPs with intensity by channels and colored by cell type
#column.names.for.umap the columns in df used for the UMAP
#cell.labels the cell labels (one label per row)
channel.UMAPs <- function(df, cell.labels, sub.sample=FALSE, n.sampling=10000){
  if (sub.sample){
    sampling.rows <- sample(1:nrow(df), n.sampling)
    df <- df[sampling.rows,]
    cell.labels <- cell.labels[sampling.rows]
  }
  
  umap_s = uwot::umap(df, n_neighbors = 50, scale=T , spread=1.5, min_dist = 0.10, n_epochs = 60)
  
  uplot = data.frame(x = umap_s[,1], y= umap_s[,2])
  pltChannels <- list()
  pltChannels <- lapply(1:ncol(df), function(x){
    markers <- df[, x]
    p = ggplot(data=uplot,aes(x,y, color=markers)) + geom_point(size=0.3, stroke=0, alpha=0.7)+ 
      #guides(color = guide_legend(override.aes = list(size=5))) + 
      theme_bw() + coord_fixed(ratio=1)+ 
      xlab("umap1") + ylab("umap2") + theme(legend.position="none") + theme(aspect.ratio=1) +
      scale_colour_gradient(low = "#103254", high="green")
    p <- p + ggtitle(colnames(df)[x])
    return(p)
  })
  
  Subtype <- factor(cell.labels, levels=unique(cell.labels))
  df <- cbind(df$Subtype)
  
  mycolors <- colorRampPalette(brewer.pal(10, "Paired"))(10)
  
  pl = ggplot(uplot,aes(x,y, color=Subtype))+ geom_point(size=0.4, stroke=0, alpha=0.7)+ 
    geom_density_2d(color="grey60", alpha=0.6) +
    scale_fill_viridis(discrete = TRUE) + 
    guides(color = guide_legend(override.aes = list(size=5))) + 
    scale_color_manual(values=mycolors) + theme_bw() + coord_fixed(ratio=1)+
    guides(colour = guide_legend(override.aes = list(size=5, shape=15, alpha=1), direction="horizontal", ncol=1, label.position="bottom", byrow=F)) + 
    xlab("umap1") + ylab("umap2") + #ylim(-10, 10) + 
    theme(legend.title = element_blank(), aspect.ratio=1)
  
  plots = list(pltChannels,pl)
  return(plots)
}

#Min max normalization
min_max_norm <- function(x) {
  (x - min(x)) / (max(x) - min(x))
}

#Robust normalization
robust_scalar<- function(x){(x- median(x)) /(quantile(x,probs = .75)-quantile(x,probs = .25))}



#####Density plots by channel name
#Channel names should match the column names
#For the input df, include only data to plot (not cell_type names or other data)
channel.densities <- function(df){
  channel.names <- colnames(df)
  pltChannels <- list()
  pltChannels <- lapply(1:ncol(df), function(x){
    mean.point=mean(df[,x])
    median.point=median(df[,x])
    p <- ggplot(df, aes_string(x=channel.names[x])) +
          geom_density() + geom_vline(xintercept=mean.point, size=1.2, color="red") +
          geom_vline(xintercept=median.point, size=1.2, color="yellow") +
          xlab("") + ggtitle(channel.names[x])
    return(p)
  })
  return(pltChannels)
}
