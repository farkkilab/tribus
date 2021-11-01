df.data = data.frame()

for(sample.name in names(labeled)) {
  sample.data = labeled[[sample.name]]
  sample.data$sample = sample.name
  sample.data[,2:56] = scale(sample.data[,2:56])#apply(sample.data[,2:56],2,scale)
  df.data = plyr::rbind.fill(df.data, sample.data)
}

df.data = df.data[,]

stroma.data = df.data[df.data$GlobalCellType=='Stromal.cells',]


# stroma.data[,54] = scale(stroma.data[,54])
# stroma.data[,54] = stroma.data[,54]-min(stroma.data[,54])
# stroma.data[,54] = stroma.data[,54]/max(stroma.data[,54])


# stroma.data[,2:56] = apply(stroma.data[,2:56],2,scale)

stroma.map = umap(stroma.data[,-c(1:5,54:66,grep('Hoech',colnames(stroma.data)))],n_threads = 20,verbose=T,y=as.factor(stroma.data$STROMAType))

p = ggplot(data=stroma.data,aes(x=stroma.map[,1],y=stroma.map[,2], col=sample)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)
 

p2 = ggplot(data=stroma.data,aes(x=stroma.map[,1],y=stroma.map[,2], col=STROMAType)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p2)



library('readxl')

naming <- data.frame(read_xlsx('sample_data.xlsx'))
naming$Cycif = sapply(naming$Cycif,function(x) paste0('Sample_',x))
naming$pub = paste0(pubID[match(substr(naming$Sample,1,4),pubID$Patient_cohort_code),2],substr(naming$Sample,5,100))

annotation_r = stroma.data$sample


tumor.data = df.data[df.data$GlobalCellType=='Tumor.cells',]
tumor.map = umap(tumor.data[,-c(1:5,54:66,grep('Hoech',colnames(stroma.data)))],n_threads = 20,verbose=T,y=as.factor(tumor.data$sample))
p = ggplot(data=tumor.data,aes(x=tumor.map[,1],y=tumor.map[,2], col=sample)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)

tumor.data$primary = naming$Sample[match(tumor.data$sample,naming$Cycif)]
tumor.primary=sub('^.{4}','',tumor.data$primary)
tumor.primary = sapply(tumor.primary,function(x)substr(x,2,2))
tumor.data$primary = as.factor(tumor.primary)

p = ggplot(data=tumor.data,aes(x=tumor.map[,1],y=tumor.map[,2], col=primary)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)

tumor.data$pfi = as.factor(naming$PFI_primary[match(tumor.data$sample,naming$Cycif)])
p = ggplot(data=tumor.data,aes(x=tumor.map[,1],y=tumor.map[,2], col=pfi)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)

tumor.data$r0 = as.factor(naming$R0_primary[match(tumor.data$sample,naming$Cycif)])
p = ggplot(data=tumor.data,aes(x=tumor.map[,1],y=tumor.map[,2], col=r0)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)

tumor.data$res = as.factor(naming$Response_primary[match(tumor.data$sample,naming$Cycif)])
p = ggplot(data=tumor.data,aes(x=tumor.map[,1],y=tumor.map[,2], col=res)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)



poster.data = df.data[df.data$sample%in%c('Sample_9','Sample_10','Sample_2','Sample_21','Sample_5','Sample_4','Sample_7','Sample_12','Sample_22','Sample_3','Sample_13','Sample_14','Sample_15','Sample_20','Sample_19'),]
pubID = read.csv('Patient_publicationID.csv',sep=';')
poster.name = poster.data$sample
poster.name = naming$Sample[match(poster.name,naming$Cycif)]
poster.name = sapply(poster.name, function(x) paste0(pubID[match(substr(x,1,4),pubID[,1]),2],substr(x,5,100)))
poster.data$sample = poster.name

stroma.data = poster.data[poster.data$GlobalCellType=='Stromal.cells',]
subsmp = sample(1:dim(stroma.data)[1],dim(stroma.data)[1]/10)
stroma.map = umap(stroma.data[subsmp,-c(1:5,54:66,grep('Hoech',colnames(stroma.data)))],n_threads = 20,verbose=T,y=as.factor(stroma.data$STROMAType[subsmp]))



p = ggplot(data=stroma.data[subsmp,],aes(x=stroma.map[,1],y=stroma.map[,2], col=sample)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)
ggsave('stroma_per_samples.png',p)


p2 = ggplot(data=stroma.data[subsmp,],aes(x=stroma.map[,1],y=stroma.map[,2], col=STROMAType)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p2)
ggsave('stroma_per_subtype.png',p2)



tumor.data = poster.data[poster.data$GlobalCellType=='Tumor.cells',]
subsmp = sample(1:dim(tumor.data)[1],dim(tumor.data)[1]/10)
tumor.map = umap(tumor.data[subsmp,-c(1:5,54:66,grep('Hoech',colnames(stroma.data)))],n_threads = 20,verbose=T,y=as.factor(tumor.data$sample[subsmp]))




p = ggplot(data=tumor.data[subsmp,],aes(x=tumor.map[,1],y=tumor.map[,2], col=sample)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)
ggsave('tumor_per_samples.png',p)

immune.data=poster.data[poster.data$GlobalCellType=='Immune.cells',]
subsmp = sample(1:dim(immune.data)[1],dim(immune.data)[1]/10)
immune.map = umap(immune.data[subsmp,-c(1:5,54:66,grep('Hoech',colnames(stroma.data)))],n_threads = 20,verbose=T,y=as.factor(immune.data$ImmuneCellType)[subsmp])
#subsmp = sample(1:dim(immune.map)[1],dim(immune.map)[1]/10)

p = ggplot(data=immune.data[subsmp,],aes(x=immune.map[,1],y=immune.map[,2], col=sample)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)
ggsave('immune_per_sample.png',p)

p = ggplot(data=immune.data[subsmp,],aes(x=immune.map[,1],y=immune.map[,2], col=ImmuneCellType)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)
ggsave('immune_per_type.png',p)

subsmp = sample(1:dim(poster.data)[1],dim(poster.data)[1]/10)

global.map = umap(poster.data[subsmp,-c(1:5,54:66,grep('Hoech',colnames(stroma.data)))],n_threads = 20,verbose=T,y=as.factor(poster.data$GlobalCellType)[subsmp],n_trees = 35)
p = ggplot(data=poster.data[subsmp,],aes(x=global.map[,1],y=global.map[,2], col=GlobalCellType)) + geom_point(size=1, stroke=0)+ guides(colour = guide_legend(override.aes = list(size=8, shape=16)))
plot(p)
ggsave('global_per_tsi.png',p)

comp.df = data.frame()

for(s in unique(poster.data$sample)){
  print(s)
  #print(pubID[match(sub("_.*","",s),pubID[,2]),1])
  tb = table(poster.data$GlobalCellType[poster.data$sample==s])
  tb = (tb/sum(tb))
  temp.df = data.frame(cycifImmune=tb[1],cycifStroma=tb[2],cycifTumor=tb[3],sample=as.character(s))
  comp.df=rbind(comp.df,temp.df)
}


##
#Heatmaps
##

hmapdata = as.data.frame(read_xlsx('heatmapdata.xlsx'))
hmap.name = hmapdata$Sample
hmap.name = sapply(hmap.name, function(x) paste0(pubID[match(substr(x,1,4),pubID[,1]),2],substr(x,5,100)))
hmapdata$Sample = hmap.name

hmapdata[match(comp.df$sample,hmapdata$Sample),c(5,6,4)]=comp.df[,1:3]*100

hmapdata = hmapdata[hmapdata$Sample%in%comp.df$sample,]

write.table(hmapdata,'heatmap.csv')

row.names(hmapdata)=hmapdata$Sample
library(pheatmap)
p=pheatmap(hmapdata[,c(2,3,4,7)],cluster_rows = F,cluster_cols = F,display_numbers = T,cellwidth = 25,cellheight = 25,angle_col = 45)
ggsave('heatmap12.png',p)

p=pheatmap(hmapdata[,c(3,4,7,10,5,8,11,6,9)],cluster_rows = F,cluster_cols = F,display_numbers = T,gaps_col = c(3,6),cellwidth = 25,cellheight = 25,angle_col = 45)
ggsave('heatmap_2.png',p)

phmapdata = hmapdata[grep('_p',hmapdata$Sample),]
clin_annot = naming[match(rownames(phmapdata),naming$pub),9:11]
clin_annot = data.frame(clin_annot)
rownames(clin_annot) = rownames(phmapdata)
clin_annot[,1] = as.factor(unlist(clin_annot[,1]))
clin_annot[,2] = as.factor(unlist(clin_annot[,2]))
clin_annot[,3] = as.factor(unlist(clin_annot[,3]))
p = pheatmap(phmapdata[,c(2,3,4,7,10,5,8,11,6,9)],cluster_rows = T,cluster_cols = F,display_numbers = T,gaps_col = c(4,7),cellwidth = 25,cellheight = 25,angle_col = 45,annotation_row = clin_annot)
ggsave('primary_hmap2.png',p,width = 10)

paired.data=hmapdata[sort(hmapdata$Sample,decreasing =T)[-c(1,6,7,14,15)],c(2,3,4,7,10,5,8,11,6,9)]
clin_annot = naming[match(rownames(paired.data),naming$pub),9:11]
clin_annot = data.frame(clin_annot)
rownames(clin_annot) = rownames(paired.data)
clin_annot[,1] = as.factor(unlist(clin_annot[,1]))
clin_annot[,2] = as.factor(unlist(clin_annot[,2]))
clin_annot[,3] = as.factor(unlist(clin_annot[,3]))

p = pheatmap(paired.data,cluster_rows = F,cluster_cols = F,display_numbers = T,gaps_col = c(4,7),gaps_row=c(2,4,6,8),cellwidth = 25,cellheight = 25,angle_col = 45,annotation_row=clin_annot)
ggsave('pair_hmap2.png',p,width = 25,units='cm')


annimu = data.frame(read_xlsx('anna_immune.xlsx'))
annimu = data.frame(scAPC = annimu$pDC+annimu$cDC2,scBcell=annimu$Plasma.B.cell+annimu$Mature.B.cell,scCD4T=annimu$CD8neg.active.T.cell+annimu$Treg,scCD8T=annimu$CD8.T.cell+annimu$CD8.T.cell.migratory+annimu$CTL,scMacrophage=annimu$Macrophage+annimu$Recruited.macrophage,sample=annimu$sample)

annimu[,1:5] = annimu[,1:5]/rowSums(annimu[,1:5])
annimu[is.na(annimu)]=0
annimu[,1:5] = annimu[,1:5]*100
bulkimu = read.table('iw.tsv',sep='\t',header = T,row.names = 1)
annimu = annimu[substr(annimu$sample,1,4)%in%substr(rownames(bulkimu),1,4),]
annimu=annimu[-c(3),]
annimu$sample = as.character(annimu$sample)
addone = is.na(sapply(sapply(annimu$sample, function(x)substr(x,nchar(x),nchar(x))),as.numeric))
annimu$sample[addone] = sapply(annimu$sample[addone],function(x)paste0(x,'1'))
addtwo = is.na(match(annimu$sample,naming$Sample))
annimu$sample[c(3,10,11,16)] = c('H091_pOvaL1','H114_pOme1','H116_iOme2','H144_pPer1')
annimu$sample = naming$pub[match(annimu$sample,naming$Sample)]

bulkimu = data.frame(bulkAPC = bulkimu[,16]+bulkimu[,20],bulkBcell=bulkimu[,15]+bulkimu[,17]+bulkimu[,19],bulkCD4T=(bulkimu[,c(3)]),bulkCD8T=bulkimu[,c(6)],bulkMacrophage=bulkimu[,12]+bulkimu[,13]+bulkimu[,14], sample=rownames(bulkimu))
bulkimu$sample=as.character(bulkimu$sample)
bulkimu$sample = sub('_[RS].*','',sub('[a:zA:Z][12]_.*','',sub('_NC','',bulkimu$sample)))
bulkimu$sample[6] = 'H114_pOme1'
bulkimu$sample = naming$pub[match(bulkimu$sample,naming$Sample)]
comp.df = data.frame()

for(s in unique(poster.data$sample)){
  print(s)
  #print(pubID[match(sub("_.*","",s),pubID[,2]),1])
  tb = table(poster.data$ImmuneCellType[poster.data$sample==s])
  tb = (tb/sum(tb))
  temp.df = data.frame(cycifAPC=tb[1],cycifBcell=tb[2],cycifCD4T=tb[3],cycifCD8T=tb[4],cycifMacrophage=tb[5],sample=as.character(s))
  comp.df=rbind(comp.df,temp.df)
  
}
comp.df[,1:5] = comp.df[,1:5]*100
annimu = annimu[match(comp.df$sample,annimu$sample),]
bulkimu = bulkimu[match(comp.df$sample,bulkimu$sample),]
bulkimu[,1:5] = bulkimu[,1:5]*100/rowSums(bulkimu[,1:5])

totimu = cbind(annimu,bulkimu,comp.df)
rownames(totimu)=totimu$sample

clin_annot = naming[match(rownames(totimu),naming$pub),9:11]
clin_annot = data.frame(clin_annot)
rownames(clin_annot) = rownames(totimu)
clin_annot[,1] = as.factor(unlist(clin_annot[,1]))
clin_annot[,2] = as.factor(unlist(clin_annot[,2]))
clin_annot[,3] = as.factor(unlist(clin_annot[,3]))
totimu = totimu[grep('_p',totimu$sample),]
p = pheatmap(totimu[,c(grep('APC',colnames(totimu)),grep('Bc',colnames(totimu)),grep('CD4',colnames(totimu)),grep('CD8',colnames(totimu)),grep('Mac',colnames(totimu)))],cluster_rows = T,cluster_cols = F,display_numbers = T,gaps_col = c(3,6,9,12),cellwidth = 25,cellheight = 25,angle_col = 45,annotation_row = clin_annot)
ggsave('immune_hmap1.png',p,width = 10)

poster.pie = poster.data[poster.data$sample%in%naming$pub[grep('95|98|102|110',naming$Sample)],]
poster.pie$cell_type=poster.pie$GlobalCellType
poster.pie$cell_type[grep('mmune',poster.pie$cell_type)] = poster.pie$ImmuneCellType[grep('mmune',poster.pie$cell_type)]
poster.pie$cell_type=as.factor(poster.pie$cell_type)
tmp.df = data.frame()
for(s in unique(poster.pie$sample)) {
  subcell = poster.pie[poster.pie$sample==s,]$cell_type
  tmp.df = rbind(tmp.df,data.frame(perc=table(subcell)/length(subcell),cell_type=names(table(subcell)),sample=s))
}
p = ggplot(tmp.df, aes(x=factor(1),y=perc.Freq, fill=cell_type)) + geom_bar(stat='identity',width=1) + coord_polar('y',start=0) + ggtitle(paste0('Composition of samples')) + ylab('Cell types') + xlab('') + scale_fill_brewer(palette="Paired") + facet_wrap(~sample)
ggsave('pies.png',p)
