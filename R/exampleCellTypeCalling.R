##############################
##  Gate calls - only names change in the phase I version below
##############################
mydata <- data3
labeled <- list()
#samples <- grep("HG0",names(data), value=TRUE)
samples <- grep("C0",names(mydata), value=TRUE)
cell.counts <- list()

for(sample.name in samples) {
  cat("Starting",sample.name,"...\n")
  t0 <- Sys.time()
  folder.name <- paste0("plots/", sample.name,"_gating")
  dir.create(folder.name, showWarnings = FALSE)
  
  # First call global cell types
  globalTypes <- cellTypeCaller(mydata[[sample.name]], global.gates2, gates.class="GlobalCellType", folder.name = folder.name)
  firstGate <- merge(x=mydata[[sample.name]], y=globalTypes, all.x=T, by="CellId")
  
  
  # Then call subtypes of immune cells
  idx <- grep('Immune', firstGate$GlobalCellType)
  firstGate$GlobalCellType[idx] <- "Immune.cells"
  print(table(firstGate$GlobalCellType))
  
  sub.df <- firstGate[which(firstGate$GlobalCellType == "Immune.cells"),]
  if(nrow(sub.df)<100) {
    cat("cellType label has less than 100 immune cells.\n")
    next
  }else {
    cat(nrow(sub.df), "Immune cells passed to next gate.\n")
  }
  # Segond gate
  immuneTypes <- cellTypeCaller(sub.df, immune.gates2, "ImmuneCellType", folder.name = folder.name)
  secondGate <- merge(x=firstGate, y=immuneTypes, all.x=T, by="CellId")
  print(table(immuneTypes$ImmuneCellType)/sum(table(immuneTypes$ImmuneCellType)))
  
  sub.df <- secondGate[which(secondGate$ImmuneCellType == "CD8.T.cells"),]
  if(nrow(sub.df)<100) {
    cat("ImmuneCellType label has less than 100 CD8+ cells.")
    thirdGate <- secondGate
  }else {
    cat(nrow(sub.df), "CD8+ cells passed to next gate.")
    # Third gate
    cd8Types <- cellTypeCaller(sub.df, cd8.gates2, "CD8TCellType", folder.name = folder.name)
    thirdGate <- merge(x=secondGate, y=cd8Types, all.x=T, by="CellId")
    print(table(cd8Types$CD8TCellType))
  }
  
  sub.df <- secondGate[which(secondGate$ImmuneCellType == "Macrophages"),]
  if(nrow(sub.df)<100) {
    cat("ImmuneCellType label has less than 100 Macrophages.")
    fourthGate <- thirdGate
  }else {
    cat(nrow(sub.df), "Macrophages passed to next gate.")
    # Third gate
    macsTypes <- cellTypeCaller(sub.df, macrophage.gates2, "MacrophageType", folder.name = folder.name)
    fourthGate <- merge(x=thirdGate, y=macsTypes, all.x=T, by="CellId")
    print(table(macsTypes$MacrophageType))
  }
  
  sub.df <- secondGate[which(secondGate$ImmuneCellType == "CD4.T.cells"),]
  if(nrow(sub.df)<100) {
    cat("ImmuneCellType label has less than 100 CD4+ cells.")
    fifthGate <- fourthGate
  }else {
    cat(nrow(sub.df), "CD4+ cells passed to next gate.")
    # fourth gate
    cd4Types <- cellTypeCaller(sub.df, cd4.gates2, "CD4TCellType", folder.name = folder.name)
    fifthGate <- merge(x=fourthGate, y=cd4Types, all.x=T, by="CellId")
    print(table(cd4Types$CD4TCellType))
  }
  
  print(table(fifthGate$ImmuneCellType)/sum(table(fifthGate$ImmuneCellType)))
  cell.counts[[sample.name]] <- table(fifthGate$ImmuneCellType)/sum(table(fifthGate$ImmuneCellType))
  
  labeled[[sample.name]] <- fifthGate
  print.xy.plot(labeled[[sample.name]], sample.name)
  # Save cellType column
  write.table(labeled[[sample.name]], paste0("gated/",sample.name,"_gated.csv"), row.names = F)
  cat('Elapsed time',Sys.time() - t0,'seconds.\n')
  tryCatch({dev.off()},error=function(cond){return(NA)})
}
