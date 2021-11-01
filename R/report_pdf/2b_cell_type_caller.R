

cellTypeCaller <- function(df, gates, gates.class="", folder.name=folder.name) {
  marker_cols <- unique(unlist(gates))
  mat <- as.matrix(df[, marker_cols])
  mat[mat<=0] <- 1 ## Quick fix because of HG0034 showing extreme bad signal. Requires detailed analyses in QC step.
  mat <- scale(mat)
  mat <- BBmisc::normalize(mat, method='range')
  data_FlowSOM <- flowCore::flowFrame(mat)
  
  n.cell.types <- length(gates)
  # set seed for reproducibility
  
  set.seed(42)
  
  # run FlowSOM
  out <- FlowSOM::ReadInput(data_FlowSOM, transform = FALSE, scale = TRUE)
  out <- FlowSOM::BuildSOM(out, colsToUse = marker_cols, silent=T, xdim=10, ydim=10)
  out <- FlowSOM::BuildMST(out, silent=T)
  # save hierarchical trees colored by markers
  
  #pdf(paste0(folder.name, "/",gates.class,"_marker_expr_by_node.pdf"))
  #for(chan in marker_cols){
  #  PlotMarker(out, chan)
  #}
  #tryCatch({dev.off()},error=function(cond){return(NA)})
  
  # Gate scores for each node
  gate.scores.by.node <- list()
  
  #tryCatch({dev.off()},error=function(cond){return(NA)})
  
  #pdf(paste0(folder.name, "/",gates.class,"_gate_score_by_node.pdf"))
  
  for(gate.name in names(gates)){
    # Transform user list into valid query format
    query <- c(rep("high", length(gates[[gate.name]]$Pos)), rep("low", length(gates[[gate.name]]$Neg)))
    names(query) <- c(gates[[gate.name]]$Pos, gates[[gate.name]]$Neg)
    # Run query for each node
    query_res = QueryStarPlot(out, query, plot = FALSE, main=gate.name)
    res <-query_res$nodeScores ## Changed in new
    res[!query_res$selected] <- min(res)
    gate.scores.by.node[[gate.name]] <- res
  }
  tryCatch({dev.off()},error=function(cond){return(NA)})
  # Normalize scores matrix between 0 and 1
  gate.scores <- do.call(cbind, gate.scores.by.node)
  nodeID.per.cell <- out$map$mapping[,1]
  #weights <- BBmisc::normalize(c(table(nodeID.per.cell)), method='range', range = c(0.75, 1))
  #centered.scores <- apply(gate.scores, 2, function(x) x - mean(x))
  normalized.scores <- BBmisc::normalize(data.frame(gate.scores, check.names = F), method='range')
  
  annotation.scores <- data.frame(normalized.scores, row.names = 1:nrow(normalized.scores))
  #annotation.scores <- data.frame(normalized.scores, row.names = 1:nrow(normalized.scores))
  #k <- (n.cell.types+2)^2
  #k <- nrow(gate.scores)/4
  k <- ceiling(100/(2/ceiling(log(2))))
  print(n.cell.types)
  print(k)
  # Median expression of the gating channels to annotate the heatmap
  medians.by.node <- aggregate(mat, by = list(out$map$mapping[,1]), median)
  
  ann_row <- data.frame(scale(medians.by.node[,-1]), row.names = 1:nrow(medians.by.node))
  if (ncol(ann_row) > 15 ) {
    ann_row <- ann_row[, order(colnames(ann_row))[1:15]]
  }
  tryCatch({dev.off()},error=function(cond){return(NA)})
  if (ncol(annotation.scores) == 1) annotation.scores$Unknown <- 1-annotation.scores[,1]
  p <- pheatmap(annotation.scores,
                show_rownames=T,show_colnames=T,cluster_rows=T,cluster_cols=T,method="ward.D2",
                cellheight=4,cellwidth=10,fontsize_row=4,fontsize_col=12,
                color=colorRampPalette(c("blue","white","red"),interpolate="linear")(300),
                border_color="white", scale='none',
                annotation_row = ann_row, cutree_rows = k, annotation_legend = FALSE)#,
                #filename =paste0(folder.name, "/",gates.class,"_normalized_scores_heatmap.pdf"))
  
  # Set labels based on clustering of scores and highest scored gate on each node
  node.class.id <- cutree(p$tree_row, k=k)
  class.mean.scores <- aggregate(annotation.scores, by=list(node.class.id), mean)[,-1]
  cutoffs <- apply(class.mean.scores, 2, min)
  class.labels <- apply(class.mean.scores, 1, function(x) {
    if(max(x) %in% cutoffs)
      "Unknown"
    else
      colnames(class.mean.scores)[which.max(x)]
  })
  node.labels <- class.labels[node.class.id]
  tryCatch({dev.off()},error=function(cond){return(NA)})
  # Asign cell type to each cell based on the node and the gate for that node
  nodeID.per.cell <- out$map$mapping[,1]
  df[,gates.class] <- class.labels[node.class.id[nodeID.per.cell]]
  
  # Plot resulting tree and compare manually to the marker trees
  #pdf(paste0(folder.name,  "/",gates.class,"_cellType_tree.pdf"))
  #PlotStars(out, backgroundValues=node.labels)
  tryCatch({dev.off()},error=function(cond){return(NA)})
  
  return(df[,c('CellId',gates.class)])
}
