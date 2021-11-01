plot_pie_charts = function(df, sample.name) {
  data.temp = df[[sample.name]]$GlobalCellType
  data.temp[which(df[[sample.name]]$GlobalCellType=='Immune.cells')] = df[[sample.name]]$ImmuneCellType[which(df[[sample.name]]$GlobalCellType=='Immune.cells')]
  data.temp[which(df[[sample.name]]$GlobalCellType=='Other2')] = 'Other'
  #if(!'NK.cells'%in%data.temp) data.temp = c(data.temp, 'NK.cells')
  data.temp = data.frame(cell.type=as.factor(data.temp))
  p = ggplot(data.temp, aes(x=factor(1), fill=cell.type)) + geom_bar(width=1) + coord_polar('y',start=0) + ggtitle(paste0('Composition of ',sample.name)) + ylab('Cell types') + xlab('') + scale_fill_brewer(palette="Paired")
  gname <- paste0("Pie_", sample.name, "_by_immuneCellType_",iteration,".pdf")
  ggsave(plot=p, filename = gname, device="pdf")
}

# This plots all charts to a single file

plot_pie_charts2 = function(df.pie) {
  data.temp = data.frame()
  for(sn in names(df.pie)) {
    tmp.df = data.frame(cell.type=df.pie[[sn]]$GlobalCellType, stringsAsFactors = F)
    tmp.df$cell.type[which(df.pie[[sn]]$GlobalCellType=='Immune.cells')] = df.pie[[sn]]$ImmuneCellType[which(df.pie[[sn]]$GlobalCellType=='Immune.cells')]
    tmp.df$cell.type[which(df.pie[[sn]]$GlobalCellType=='Other2')] = 'Other'
    #if(!'NK.cells'%in%tmp.df$cell.type) tmp.df = rbind(tmp.df, 'NK.cells')
    cells = table(tmp.df)
    tmp.df = data.frame(cell.counts=as.integer(cells),cell.type=names(cells))
    tmp.df$perc = tmp.df$cell.counts/sum(tmp.df$cell.counts)
    tmp.df$name = sn
    data.temp = rbind(data.temp, tmp.df)
  }
  
  #data.temp$cell.type = as.factor(data.temp$cell.type)
  p = ggplot(data.temp, aes(x=factor(1), y=perc, fill=cell.type)) + geom_bar(stat='identity',width=1) + coord_polar('y',start=0) + ggtitle(paste0('Composition of samples')) + ylab('Cell types') + xlab('') + scale_fill_brewer(palette="Paired") + facet_wrap(~name)
  gname <- paste0("Pie_by_immuneCellType_",iteration,".pdf")
  ggsave(plot=p, filename = gname, device="pdf")
}

# This takes two different datasets that have been ran through celltypecaller to compare the results
# Markerindex is calculated for the latter dataset.
# You should be able to run it by supplying one dataset twice if you don't want to compare
plot_qc_plot = function(df.qc, df.new) {
  print('Checking changes in unknown cell types')
  rows = sapply(df.qc, nrow)
  rows.new = sapply(df.new, nrow)
  df.qc = lapply(df.qc, combine.gates)
  df.new = lapply(df.new, combine.gates)
  others = sapply(df.qc, function(x)sum(is.na(x$cell.type)))
  others = others/rows
  others.new = sapply(df.new, function(x)sum(is.na(x$cell.type)))
  others.new = others.new/rows.new
  
  others = data.frame(amount=as.numeric(others), sample=names(others), iteration=rep(old.iteration))
  others.new = data.frame(amount=as.numeric(others.new), sample=names(others.new), iteration=rep(iteration))
  others = rbind(others,others.new)
  p = ggplot(others, aes(x=sub('Sample_','',sample), y=amount,fill=iteration)) + geom_bar(stat = 'identity',position="dodge2") + xlab('Sample number') + ylab('Proportion of "other" cells')
  gname <- paste0("OtherTypes_",iteration,".pdf")
  ggsave(plot=p, filename = gname, device="pdf")
  print('Done')
  
  
  print('Calculating differences in gateindex')
  gateindex = data.frame()
  markerindex = data.frame()
  #colnames(gateindex) = c('cell.type', 'index', 'iteration','sample')
  print('Processing the first dataset')
  indices = index_sample(df.qc, old.iteration)
  markerindex = rbind(markerindex, indices[[1]])
  gateindex = rbind(gateindex, indices[[2]])
  
  print('Processing the second dataset')
  indices = index_sample(df.new, iteration)
  indices[[1]] = add_missing_cols(markerindex, indices[[1]])
  indices[[2]] = add_missing_cols(gateindex, indices[[2]])
  
  markerindex = rbind(add_missing_cols(indices[[1]],markerindex), indices[[1]])
  gateindex = rbind(add_missing_cols(indices[[2]],gateindex), indices[[2]])
  

  
  # Scale the baseline to 1 and show the change as percentage
  #print('Scaling')
  #for(sample.name in gateindex$sample) {
  #  for(cell.name in gateindex[gateindex$sample==sample.name,]$cell.type) {
  #    subs = gateindex[gateindex$sample==sample.name&gateindex$cell.type==cell.name,]
  #    if(old.iteration %in% subs$iteration & iteration%in%subs$iteration) {
  #      gateindex[gateindex$sample==sample.name&gateindex$cell.type==cell.name&gateindex$iteration==iteration,]$index = gateindex[gateindex$sample==sample.name&gateindex$cell.type==cell.name&gateindex$iteration==iteration,]$index / gateindex[gateindex$sample==sample.name&gateindex$cell.type==cell.name&gateindex$iteration==old.iteration,]$index
  #    }
  #    if(old.iteration %in% subs$iteration) gateindex[gateindex$sample==sample.name&gateindex$cell.type==cell.name&gateindex$iteration==old.iteration,]$index = 1
  #    
  #  }
  #}
  
  
  p = ggplot(gateindex, aes(x=cell.type, y=index, col=iteration)) + geom_point() +ggtitle(paste0('Gate index')) + theme(axis.text.x = element_text(angle = 45, hjust = 1,size = 5)) + facet_wrap(~sample) + geom_hline(yintercept=0)
  gname <- paste0("GateIndex_by_CellType_",iteration,".pdf")
  ggsave(plot=p, filename = gname, device="pdf")
  
  mi = find_wrong_gates(markerindex)
  p = ggplot(mi, aes(x=marker, y=index,col=iteration)) + geom_point() +ggtitle(paste0('Marker index')) + theme(axis.text.x = element_text(angle = 45, hjust = 1,size = 5)) + facet_wrap(~cell.type) + geom_hline(yintercept=0)
  gname <- paste0("MarkerIndex_by_CellType_",old.iteration,".pdf")
  ggsave(plot=p, filename = gname, device="pdf")
  
  
}


get_index = function(means.ct, rn) {
  row.names(means.ct) = rn
  gi = data.frame()
  for(cell.name in rownames(means.ct)[-(which(rownames(means.ct)=='Unknown'))]) {
    if(cell.name%in%c('Tumor.cells','Stromal.cells')) gates = global.gates
    else gates = immune.gates
    pos = gates[[gsub('[.]',' ',cell.name)]][['Pos']]
    neg = gates[[gsub('[.]',' ',cell.name)]][['Neg']]
    
    if(cell.name=='Stromal.cells') {
      tmp.gates = unlist(gates[grep('Stroma',names(gates))])
      pos = unique(tmp.gates[grep('Pos', names(tmp.gates))])
      neg = unique(tmp.gates[grep('Neg', names(tmp.gates))])
    }
    if(cell.name=='Langerhans.cell') {
      next
    }
    if(cell.name=='Innate.like.T.cells') {
      next
    }
    neg = neg[which(neg%in%colnames(means.ct))]
    pos = pos[which(pos%in%colnames(means.ct))]
    gi = rbind(gi, data.frame(index = sum(means.ct[cell.name,pos])-sum(means.ct[cell.name,neg]), cell.type=cell.name))
  }
  return(gi)
}

find_wrong_gates = function(df) {
  # There must be a better way of doing things
  gate_summary = data.frame()
  for(iteration in unique(as.character(df$iteration))) {
    df.iter = df[df$iteration==iteration,]
    for(cell.name in unique(as.character(df.iter$cell.type))) {
      df.cell = df.iter[which(df.iter$cell.type==cell.name),]
      for(marker in colnames(df))
        if(!marker %in% c('sample', 'cell.type','iteration')){
          df.marker = df.cell[,marker]
          gate_summary = rbind(gate_summary, data.frame(cell.type = cell.name, marker = marker, index = mean(df.marker),iteration=iteration))
        }
    }
  }
  return(gate_summary)
}

plot_umaps = function(lbld) {
  for(sample.name in names(lbld)) {
    sample.data = lbld[[sample.name]]
    # Take only 30% of cells to make the clustering faster
    cells_to_keep = sample(1:nrow(sample.data), floor(nrow(sample.data)/3))
    subdf = sample.data[cells_to_keep,1:(which(colnames(sample.data)=='Area')-1)]
    #Cluster only with the markers used in gating
    subdf = cbind(subdf[,1],subdf[,which(marker.in.gates(colnames(subdf)))])
    # Ignore background
    subdf = subdf[,which(!colnames(subdf)%in%c('Mouse','Goat','Rabbit'))]
    # Adjust these parameters!
    umap_s = uwot::umap(subdf[,-1], n_neighbors = 5, verbose = TRUE, n_threads = 7, fast_sgd = TRUE, min_dist = 0.001,metric = "euclidean", y=as.factor(sample.data$GlobalCellType[cells_to_keep]))
    
    # Color by ctc calls
    indices = match(subdf[,1],sample.data$CellId)
    indices = indices[!is.na(indices)]
    ctc = combine.gates(sample.data[indices,])$cell.type
    
    
    uplot = data.frame(x = umap_s[,1], y= umap_s[,2],call =ctc )
    p = ggplot(uplot,aes(x,y,color=call))+ geom_point(size=1, stroke=0, shape='.')
    ggsave(plot=p, filename = paste0('umap_',sample.name,'_',iteration,'.pdf'), device="pdf")
  }
  
}

index_sample = function(df, iterat){
  gateindex = data.frame()
  markerindex = data.frame()
  for(sample.name in names(df)){ 
    means.by.cell.type <- get_means(sample.name, df)
    rs = row.names(means.by.cell.type)
    means.by.cell.type= data.frame(means.by.cell.type %>% mutate_all(scale))
    means.ct = means.by.cell.type
    means.ct$sample = sample.name
    means.ct$cell.type = rs
    means.ct$iteration = iterat
    markerindex = rbind(markerindex, means.ct)
    gi = get_index(means.by.cell.type, rs)
    
    gi$iteration = iterat
    gi$sample = sample.name
    gateindex = rbind(gateindex,gi)
  }
  return(list(markerindex, gateindex))
}

plot_heatmaps = function(labeled, functionals=FALSE){
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

get_means = function(sample.name, data.tmp,functionals) {
  cols <- grep(paste0("Id|",dnachannel,"|",bgchannels), colnames( data.tmp[[sample.name]]), invert = T, value = T)
  maxi <- which(cols == "Area")-1
  cols <- cols[1:maxi]
  #res <- data.tmp[[sample.name]] %>% group_by(cell.subtype) %>% summarise_at(.vars=cols, .funs=mean) ## change to median
  res <- data.tmp[[sample.name]] %>% group_by(cell.type) %>% summarise_at(.vars=cols, .funs=mean) ## change to median
  #res[1,1] <- "Other"
  res[which(is.na(res[,1])),1] <- 'Unknown'
  #if (sample.name == "Sample_13") {
  #  for(lbl in c('CD45RO','FOXP3','CD3d')){
  #    mincro <- min( res[[lbl]][res[lbl]!=min(res[lbl])] )
  #    res[[lbl]][which(is.infinite(res[[lbl]]))] <- mincro
  #  }
  #}
  return(data.frame(res[,-1][,marker.in.gates(colnames(res[,-1]),functionals)], row.names = res$cell.type))
}

plot.heatmap <- function(data, scalem="none", title=NULL, fname=NA, ann_col=NULL, ann_row=NULL, colors=NULL) {
  #mat <- scale( as.matrix(data) )
  pheatmap(as.matrix(data),
           show_rownames=T,show_colnames=T,cluster_rows=T,cluster_cols=T,
           cellheight=12,cellwidth=12,fontsize_row=12,fontsize_col=12,
           color=colorRampPalette(c("#0e74b3","white","#cf242a"),interpolate="linear")(200),
           border_color="white", annotation_col=ann_col, annotation_colors = colors,
           annotation_row=ann_row,
           scale=scalem, filename=fname, height=12, main = title)
}

# Function required for some plotting methods
combine.gates <- function(df) {
  #df <- labeled[[sample.name]]
  df$cell.type <- df$GlobalCellType
  df$cell.type[which(df$GlobalCellType=="Immune.cells")] <- df$ImmuneCellType[which(df$GlobalCellType=="Immune.cells")]
  #df$cell.type[which(df$GlobalCellType=="Tumor.cells")] <- df$tumorType[which(df$GlobalCellType=="Tumor.cells")]
  df$cell.type[ which(df$cell.type == "Other")] <- NA
  df$cell.type[ which(df$cell.type == "Other2")] <- NA
  df$cell.type[ which(df$cell.type == "Unknown")] <- NA
  return(df)
}

detailed.gates <- function(df) {
  df$cell.subtype <- df$cell.type
  if('CD8TCellType' %in% colnames(df))
    df$cell.subtype[which(df$cell.type=="CD8.T.cells")] <- df$CD8TCellType[which(df$cell.type=="CD8.T.cells")]
  if('MacrophageType' %in% colnames(df))
    df$cell.subtype[which(df$cell.type=="Macrophages")] <- df$MacrophageType[which(df$cell.type=="Macrophages")]
  if('CD4TCellType' %in% colnames(df))
    df$cell.subtype[which(df$cell.type=="CD4.T.cells")] <- df$CD4TCellType[which(df$cell.type=="CD4.T.cells")]
  if('CD4Type' %in% colnames(df))
    df$cell.subtype[which(df$cell.type=="CD4.T.cells")] <- df$CD4Type[which(df$cell.type=="CD4.T.cells")]
  df$cell.subtype[ which(df$cell.type == "Other")] <- NA
  df$cell.subtype[ which(df$cell.type == "Other2")] <- NA
  df$cell.subtype[ which(df$cell.subtype == "CD4.T.cells")] <- "CD4.effector.T.cells"
  df$cell.subtype[ which(df$cell.type == "Unknown")] <- NA
  df$cell.subtype[ which(df$cell.subtype == "CD8.T.cells")] <- "CD8.effector.T.cells"
  return(df)
}

# Couple of required plotting functions
save.corrplot <- function(df, marker_cols){
  p.cor <- cor(as.matrix(as.matrix(df[, marker_cols])) , method="spearman")
  corrplot(p.cor, method="shade", shade.col=NA, col=colorRampPalette(c("blue","white","red"), interpolate="spline")(200), addrect=3, tl.col="black", order="hclust", hclust.method = "ward.D2", tl.srt=45)
  corrplot(p.cor, add=T, type="lower", col=colorRampPalette(c("blue","white","red"), interpolate="spline")(200),method="number",addrect=3,  number.cex = 0.5, order="hclust", hclust.method = "ward.D2", diag=F, tl.pos = 'n', cl.pos='n')
}


print.xy.plot <- function(df, sample.name, base.or.immune =T){ 
  df$cell.type <- df$GlobalCellType
  if(base.or.immune) df$cell.type[which(df$GlobalCellType=="Immune.cells")] <- df$ImmuneCellType[which(df$GlobalCellType=="Immune.cells")]
  #df$cell.type[which(df$GlobalCellType=="Tumor.cells")] <- df$tumorType[which(df$GlobalCellType=="Tumor.cells")]
  df$cell.type[which(df$GlobalCellType=="Stromal.cells")] <- "Stromal.cells"#ifelse(df$STROMAType[which(df$GlobalCellType=="Stromal.cells")]=='Endothelial.cell','Endothelial.cell','Stromal.cell')
  df$cell.type[ which(df$cell.type == "Other2")] <- NA
  df$cell.type[ which(df$cell.type == "Other")] <- NA
  df$cell.type[ which(df$cell.type == "Unknown")] <- NA
  
  table(df$cell.type)
  ntypes <- length(unique(df$cell.type))
  mycolors <- colorRampPalette(brewer.pal(8, "Set2"))(ntypes)
  
  p <- ggplot(df, aes(x=X_position, y=Y_position, color=cell.type)) + geom_point(size=1, stroke=0, shape='.') + scale_color_manual(values=mycolors, na.value = "grey50") + theme_bw() + ggtitle(sample.name) + coord_fixed(ratio = 1) + scale_y_reverse() + guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
  gname <- paste0("XY_", sample.name, "scatter_by_",ifelse(!base.or.immune,'global','immune'),"CellType_",iteration,".pdf")
  ggsave(plot=p, filename = gname, device="pdf")
}

add_missing_cols = function(df.new, df.old) {
  newinold = which(is.na(match(colnames(df.new),colnames(df.old))))
  if(length(newinold)>0) {
    for(i in newinold) {
      cn = colnames(df.old)
      print(colnames(df.new)[i])
      print(colnames(df.old)[i])
      df.old = cbind(df.old[,0:(i-1)],df.new[,i],df.old[,i:(ncol(df.old))])
      colnames(df.old) = c(cn[0:(i-1)],colnames(df.new)[i],cn[i:ncol(df.old)])
    }
  }
  return(df.old)
}
# This function requires you to source the gates to memory and to have gates with the names global.gates and immune.gates
marker.in.gates = function(x,functionals=FALSE){
  included = x%in%unlist(global.gates)|x%in%unlist(immune.gates) #|x%in%unlist(stroma.gates))
  if(functionals) included = !included
  return(included)
}