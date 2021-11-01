global.gates <- list()
global.gates[["Tumor cells"]] <- list(
  Pos=c('CK7','Ecadherin'),
  Neg=c('CD3d','Desmin','CD163','CD68','Vimentin'))
global.gates[["Immune cells1"]] <- list(
  Pos=c('CD3d','CD45RO','CD8a','CD4'),
  Neg=c('CK7','Ecadherin','SMA', 'Mouse','Rabbit','Goat','CD31'))
global.gates[["Immune cells2"]] <- list(
  Pos=c('CD11c','MHCII','CD11b','IBA1'),
  Neg=c('CK7','SMA','Mouse','Goat','Rabbit','CD31','Ecadherin'))
#global.gates[["Immune cells3"]] <- list(
#  Pos=c('CD11b'),
#  Neg=c('CK7','SMA','Mouse','Goat','Rabbit','Ecadherin'))
#global.gates[["Immune cells4"]] <- list(
#  Pos=c('CD20', 'MHCII'),
#  Neg=c('CD11b','CD4','CD8a','CD3d','CD163','CD11c','CD207','CK7','Ecadherin','Mouse','Rabbit','Goat','CD15','CD31','Vimentin','Desmin','CD57','SMA'))
#global.gates[["Immune cells5"]] <- list(
#  Pos=c('CD4', 'CD45RO'),
#  Neg=c('CK7','Ecadherin','SMA', 'Goat','CD31','CD8a','CD3d'))
global.gates[["Stromal cells1"]] <- list(
  Pos=c('Desmin','Vimentin','SMA','CD31'),
  Neg=c('CD163','CD3d','CD20','CD8a','CD15','CD11c','CD11b', 'Rabbit', 'Mouse', 'Goat','CK7','Ecadherin'))
#global.gates[["Stromal cells1"]] <- list(
#  Pos=c('Desmin'),
#  Neg=c('CD163','CD3d','CD20','CD8a','CD15','CD11c','CD11b', 'Rabbit', 'Mouse', 'Goat','CK7','Ecadherin'))
#global.gates[["Stromal cells2"]] <- list(
#  Pos=c('SMA','Vimentin','pSTAT1'),
#  Neg=c('CD163','CD3d','CD20','CD8a','CD15','CD11c','CD11b','CK7','Ecadherin'))
#global.gates[["Stromal cells3"]] <- list(
#  Pos=c('CD31'),
#  Neg=c('CD163','CD3d','CD20','CD8a','CD15','CD207','CD11c','CD11b', 'Rabbit', 'Mouse', 'Goat','CK7','Ecadherin'))
global.gates[["Other"]] <- list(
  Pos=c('Rabbit', 'Mouse', 'Goat'),
  #Neg=c('Ecadherin','CD57','SMA','CD68','CD4','CD20','CD8a','CD207','CD11c','CD163','CD15','CD11b'))
  Neg=unique(unlist(lapply(global.gates, function(x) x$Pos))))
global.gates[["Other2"]] <- list(
  Pos=c(),
  Neg=unique(unlist(lapply(global.gates, function(x) c(x$Neg,x$Pos)))))
  

immune.gates <- list()
immune.gates[["CD8 T cells"]] <- list(
  Pos=c('CD8a','CD3d'),
  Neg=c('CD4','CD20','CD163','CD15','CD68','CD207'))
immune.gates[["CD4 T cells"]] <- list(
  Pos=c('CD4','CD3d'),
  Neg=c('CD8a','CD163','CD20','CD15','CD68', 'CD11c','CD11b','IBA1','CD207','CD57'))
immune.gates[["Macrophages"]] <- list(
  Pos=c('CD11b','CD68','CD163', 'IBA1'),
  Neg=c('CD20','CD3d','CD57','CD207','CK7','CD11c','CD15'))
immune.gates[["B cells"]] <- list(
  Pos=c('CD20','MHCII','Vimentin','MHCI'),
  Neg=c('CD11b','CD4','CD8a','CD3d','CD163','CD11c','CD207','CK7','Ecadherin','Mouse','Rabbit','Goat','CD15','CD31','Desmin','CD57','SMA'))
immune.gates[["Antigen presenting cells"]] <- list(
  Pos=c('CD207','CD11c','MHCII'),
  Neg=c('CD4','CD20','CD8a','CD57','CD3d','CD163','CK7','CD15'))
#immune.gates[["NK cells"]] <- list(
#  Pos=c('CD57'),
#  Neg=c('CD4','CD20','CD163','CD8a','CK7','Ecadherin','Mouse','Rabbit','CD15','IBA1','CD68','CD31'))
#immune.gates[["Neutrophils"]] <- list(
#  Pos=c('CD15'),
#  Neg=c('CD4','CD20','CD8a','CD57','CD3d','CD163','CK7','CD68','Ecadherin','MHCII','CD57','CD31'))
immune.gates[["Other"]] <- list(
  Pos=c(),
  Neg=c('CD11b','CD4','CD20','CD8a','CD57','CD163','CD68','CD15','CD3d', 'CD11c'))

cd8.gates <- list()
cd8.gates[["Memory CD8 T cells"]] <- list(
  Pos=c('CD45RO','CD8a','CD3d'),
  Neg=c())
cd8.gates[["CD8 effector T cells"]] <- list(
  Pos=c('CD8a','CD3d'),
  Neg=c('CD45RO'))

cd4.gates <- list()
cd4.gates[["CD4 effector T cells"]] <- list(
  Pos=c('CD4','CD3d'),
  Neg=c('FOXP3'))
cd4.gates[["T regulatory cells"]] <- list(
  Pos=c('FOXP3','CD4','CD3d'),
  Neg=c())
cd4.gates[["Memory CD4 T cells"]] <- list(
  Pos=c('CD45RO','CD4','CD3d'),
  Neg=c('FOXP3'))


macrophage.gates <- list()
macrophage.gates[["CD11b CD68 Macrophages"]] <- list(
  Pos=c('CD11b','CD68'),
  Neg=c('CD163', 'CD11c','CD20'))
macrophage.gates[["CD163 Macrophages"]] <- list(
  Pos=c('CD163','CD11b'),
  Neg=c('CD11c'))
macrophage.gates[["TIM3 Macrophages"]] <- list(
  Pos=c('CD11b','TIM3'),
  Neg=c('CD11c'))

dc.gates <- list()
dc.gates[['CD207 APC cell']]<- list(
  Pos=c('CD207','CD11c', 'Ecadherin'),
  Neg=c('CD11b'))
dc.gates[['CD11cCd11b DC cell']]<- list(
  Pos=c('CD11c','CD11b'),
  Neg=c())
dc.gates[['CD11c DC cell']]<- list(
  Pos=c('CD11c'),
  Neg=c('CD11b'))

stroma.gates <- list()
stroma.gates[['Endothelial cell']] <- list(
  Pos=c('CD31'),
  Neg=c('CD3d','Vimentin','SMA','Desmin'))
stroma.gates[['Myofibroblast']] <- list(
  Pos=c('SMA','Vimentin'),
  Neg=c('Desmin','CD31'))
stroma.gates[['Mesothelial cell']] <- list(
  Pos=c('Desmin'),
  Neg=c('SMA','CD31'))
stroma.gates[['Interferon activated stroma']] <- list(
  Pos=c('Vimentin', 'pSTAT1'),
  Neg=c('CD31'))

tumor.gates <- list()
tumor.gates[['Langerhans cell']] <- list(
  Pos=c('CD207','Ecadherin'),
  Neg=c('CK7'))
tumor.gates[['Tumor cells']] <- list(
  Pos=c('CK7','Ecadherin'),
  Neg=c())


#marker.in.gates = function(x,functionals=FALSE){
#  included = x%in%unlist(global.gates)|x%in%unlist(immune.gates) #|x%in%unlist(stroma.gates))
#  if(functionals) included = !included
#  return(included)
#}
