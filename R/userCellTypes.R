global.gates <- list()
global.gates[["Tumor cells"]] <- list(
  Pos=c('CK7','Ecadherin','PAX8'),
  Neg=c('CD3d','CD4','CD8a','CD15','CD207','CD1c','IBA1','CD20','SMA', 'Background488', 'Background555', 'Background647'))
global.gates[["Immune cells1"]] <- list(
  Pos=c('CD3d'),
  Neg=c('CK7','Ecadherin','PAX8','SMA', 'Background555'))
global.gates[["Immune cells2"]] <- list(
  Pos=c('CD207','CD1c'),
  Neg=c('CK7','Ecadherin','PAX8','SMA','Background555','Background647'))
global.gates[["Immune cells3"]] <- list(
  Pos=c('IBA1'),
  Neg=c('CK7','Ecadherin','PAX8','SMA','Background488'))
global.gates[["Immune cells4"]] <- list(
  Pos=c('CD20'),
  Neg=c('CK7','Ecadherin','PAX8','SMA','Background647'))
global.gates[["Stromal cells"]] <- list(
  Pos=c('SMA','Vimentin'),
  Neg=c('PAX8','CD3d','CD20','CD8a','CD15','CD207','CD1c','IBA1', 'Background488', 'Background555', 'Background647'))
global.gates[["Other"]] <- list(
  Pos=c('Background488', 'Background555', 'Background647'),
  Neg=c('Ecadherin','CD57','SMA','IBA1','CD4','CD20','CD8a','CD207','CD1c','CD163','CD15','CD11b'))

immune.gates <- list()
immune.gates[["CD8 T cells"]] <- list(
  Pos=c('CD8a','CD3d'),
  Neg=c('CD4','CD20','CD163'))
immune.gates[["CD4 T cells"]] <- list(
  Pos=c('CD4','CD3d'),
  Neg=c('CD8a','CD163','CD20'))
immune.gates[["Macrophages"]] <- list(
  Pos=c('IBA1','CD11b','CD163'),
  Neg=c('CD20','CD8a','CD3d','CD57','CD207','CK7','Ecadherin','PAX8'))
immune.gates[["B cells"]] <- list(
  Pos=c('CD20'),
  Neg=c('IBA1','CD4','CD8a','CD3d','CD163','CD1c','CD207','CK7','Ecadherin','PAX8'))
immune.gates[["Antigen presenting cells"]] <- list(
  Pos=c('CD207','CD1c'),
  Neg=c('IBA1','CD4','CD20','CD8a','CD57','CD3d','CD163','CK7','Ecadherin','PAX8'))
immune.gates[["NK cells"]] <- list(
  Pos=c('CD57'),
  Neg=c('PD1','IBA1','CD4','CD20','CD163','CD8a','CD1c','CD207','CK7','Ecadherin','PAX8'))
immune.gates[["Neutrophils"]] <- list(
  Pos=c('CD15'),
  Neg=c('IBA1','CD4','CD20','CD8a','CD57','CD3d','CD163','CD207','CK7','CD11b','CD1c','Ecadherin','PAX8'))
immune.gates[["Other"]] <- list(
  Pos=c(),
  Neg=c('IBA1','CD4','CD20','CD8a','CD57','CD163','CD11b','CD15','CD3d', 'CD1c'))

cd8.gates <- list()
cd8.gates[["Exhausted CD8 T cells"]] <- list(
  Pos=c('PD1','CD8a','CD3d'),
  Neg=c())
cd8.gates[["CD8 effector T cells"]] <- list(
  Pos=c('CD8a','CD3d'),
  Neg=c('PD1'))

cd4.gates <- list()
cd4.gates[["CD4 effector T cells"]] <- list(
  Pos=c('CD4','CD3d'),
  Neg=c('FOXP3'))
cd4.gates[["T regulatory cells"]] <- list(
  Pos=c('FOXP3','CD4','CD3d'),
  Neg=c())

macrophage.gates <- list()
macrophage.gates[["IBA1 CD11b Macrophages"]] <- list(
  Pos=c('CD11b','IBA1'),
  Neg=c('CD163'))
macrophage.gates[["CD163 Macrophages"]] <- list(
  Pos=c('CD163','IBA1'),
  Neg=c('CD11b'))

####################################
# PHASE II - Gates and gate calls
####################################
global.gates2 <- global.gates
immune.gates2 <- immune.gates
cd8.gates2 <- cd8.gates
cd4.gates2 <- cd4.gates
macrophage.gates2 <- macrophage.gates

global.gates2 <- list()
global.gates2[["Tumor cells"]] <- list(
  Pos=c('CK7','Ecadherin','PAX8'),
  Neg=c('CD3d','CD4','CD8a','CD15','CD207','CD11c','IBA1','CD20','CD31', 'Background488', 'Background555', 'Background647'))
global.gates2[["Immune cells1"]] <- list(
 Pos=c('CD3d'),
 Neg=c('CK7','Ecadherin','PAX8','CD31', 'Background555'))
global.gates2[["Immune cells2"]] <- list(
 Pos=c('CD207','CD11c'),
 Neg=c('CK7','Ecadherin','PAX8','CD31','Background555','Background647'))
global.gates2[["Immune cells3"]] <- list(
 Pos=c('IBA1'),
 Neg=c('CK7','Ecadherin','PAX8','CD31','Background488'))
global.gates2[["Immune cells4"]] <- list(
 Pos=c('CD20'),
 Neg=c('CK7','Ecadherin','PAX8','CD31','Background647'))

global.gates2[["Stromal cells"]] <- list(
  Pos=c('CD31','Vimentin'),
  Neg=c('PAX8','CD3d','CD20','CD207','CD11c','IBA1', 'Background488', 'Background555', 'Background647'))
global.gates2[["Other"]] <- list(
  Pos=c('Background488', 'Background555', 'Background647'),
  Neg=c('Ecadherin','CD57','CD31','IBA1','CD4','CD20','CD8a','CD207','CD11c','CD163','CD15','CD11b'))

immune.gates2 <- list()
immune.gates2[["CD8 T cells"]] <- list(
  Pos=c('CD8a','CD3d'),
  Neg=c('CD4','CD20','CD163'))
immune.gates2[["CD4 T cells"]] <- list(
  Pos=c('CD4','CD3d'),
  Neg=c('CD8a','CD163','CD15'))
immune.gates2[["Macrophages"]] <- list(
  Pos=c('IBA1','CD11b','CD163'),
  Neg=c('CD8a','CD3d','CD57','CD207','CK7','Ecadherin','PAX8'))
immune.gates2[["B cells"]] <- list(
  Pos=c('CD20'),
  Neg=c('IBA1','CD4','CD8a','CD3d','CD163','CD11c','CD207','CK7','Ecadherin','PAX8'))
immune.gates2[["Antigen presenting cells"]] <- list(
  Pos=c('CD207','CD11c'),
  Neg=c('IBA1','CD4','CD20','CD8a','CD57','CD3d','CD163','CK7','Ecadherin','PAX8'))
immune.gates2[["NK cells"]] <- list(
  Pos=c('CD57'),
  Neg=c('PD1','CD45RO','IBA1','CD4','CD20','CD163','CD8a','CD11c','CD207','CK7','Ecadherin','PAX8'))
immune.gates2[["Neutrophils"]] <- list(
  Pos=c('CD15'),
  Neg=c('IBA1','CD4','CD20','CD8a','CD57','CD3d','CD163','CD207','CK7','CD11b','CD11c','Ecadherin','PAX8'))
immune.gates2[["Other"]] <- list(
  Pos=c(),
  Neg=c('IBA1','CD4','CD20','CD8a','CD57','CD163','CD11b','CD15','CD3d', 'CD11c'))
immune.gates2[["Dump0032"]] <- list(
  Pos=c("PAX8","CD20"),
  Neg=c("CK7"))

cd8.gates2 <- list()
cd8.gates2[["Exhausted CD8 T cells"]] <- list(
  Pos=c('PD1','CD8a','CD3d'),
  Neg=c('CD45RO'))
cd8.gates2[["CD8 T memory cells"]] <- list(
  Pos=c('CD45RO','CD3d','CD8a'),
  Neg=c('PD1'))
cd8.gates2[["CD8 effector T cells"]] <- list(
  Pos=c('CD8a','CD3d'),
  Neg=c('PD1','CD45RO'))

######## GATES FOR C0138

immune.gates2 <- list()
immune.gates2[["CD8 T cells"]] <- list(
  Pos=c('CD8a','CD3d'),
  Neg=c('CD4','CD163','CD57','CD15','IBA1','CD207','PAX8','CD31'))
immune.gates2[["CD4 T cells"]] <- list(
  Pos=c('CD4','CD3d'),
  Neg=c('CD8a','CD163','CD15'))
immune.gates2[["Macrophages"]] <- list(
  Pos=c('IBA1','CD11b','CD163'),
  Neg=c('CD8a','CD3d','CD57','CD207','CK7','Ecadherin','PAX8'))
immune.gates2[["B cells"]] <- list(
  Pos=c('CD20'),
  Neg=c('IBA1','CD4','CD8a','CD57','CD11b','CD3d','CD163','CD11c','CD207','CK7','Ecadherin','PAX8'))
immune.gates2[["Antigen presenting cells"]] <- list(
  Pos=c('CD207','CD11c'),
  Neg=c('IBA1','CD4','CD20','CD8a','CD57','CD3d','CD163','CK7','Ecadherin','PAX8'))
immune.gates2[["NK cells"]] <- list(
  Pos=c('CD57'),
  Neg=c('PD1','CD45RO','IBA1','CD4','CD20','CD163','CD8a','CD11c','CD207','CK7','Ecadherin','PAX8'))
immune.gates2[["Neutrophils"]] <- list(
  Pos=c('CD15'),
  Neg=c('IBA1','CD4','CD20','CD8a','CD57','CD3d','CD163','CD207','CK7','CD11b','CD11c','Ecadherin','PAX8'))
immune.gates2[["Other"]] <- list(
  Pos=c(),
  Neg=c('IBA1','CD4','CD20','CD8a','CD57','CD163','CD11b','CD15','CD3d', 'CD11c'))
## create dump gate
immune.gates2[['Dump0138']] <- list(
  Pos=c('CD20','CD57','CD11b','CD8a'),
  Neg=c())
