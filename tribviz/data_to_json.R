# convert csv files to json for vitessce
# Example for two samples
library(jsonlite)
library(uwot)


data1 = read.csv("s21_gated.csv", sep = " ", header = T)
data2 = read.csv("s23_gated.csv", sep = " ", header = T)

source("I:/tribus/tribus/R/tribviz/ang_gates.r")

pos.markers = unique(unlist(lapply(global.gates[1:4],function(x) x$Pos)))

cols.to.keep = c("ID", "X_position", "Y_position", pos.markers, "GlobalCellType", "Sample")

data1$Sample = "S21"
data2$Sample = "S23"

dataw = rbind(data1,data2)

dataw = dataw[,cols.to.keep]

idindex = 1
xindex = 2
yindex = 3
celltypeindex = ncol(dataw)-1
sampleindex = ncol(dataw)

um = umap(dataw[,-c(idindex,xindex,yindex,celltypeindex,sampleindex)])

dataw$UmapX = um[,1]
dataw$UmapY = um[,2]


toVitJson = function(df) {
  json.str = apply(df,1,serializer,colnames(df))
  merged.str = paste(json.str, collapse = '')
  result.str = paste0("{",sub(",$","",merged.str),"}")
  return(result.str)
}


# Custom serializer function to create nice json for vitessce
serializer = function(x, cnames) {
  # Remove ID, x,y and celltype,sample from the markerset
  # indices are hardcoded for this specific dataset
  idindex = 1
  xindex = 2
  yindex = 3
  celltypeindex = length(x)-3
  sampleindex = length(x)-2
  umapindexx = length(x)-1
  umapindexy = length(x)
  x = as.data.frame(t(x))
  colnames(x) = cnames
  markers = toJSON(x[-c(idindex,xindex,yindex,celltypeindex,sampleindex,umapindexx,umapindexy)])
  markers = as.character(markers)
  markers = substr(markers, 3, nchar(markers)-2)
  genes = gsub(",", ",\\1\n    ",markers)
  paste0("\"cell_",x[sampleindex],".",as.numeric(x[idindex]),"\":{
  \"mappings\": {
    \"UMAP\":[
      ",x[umapindexx],",
      ",x[umapindexy],"]
  },
  \"genes\": {
    ",genes,"
  },
  \"xy\": [
    ",x[xindex],",
    ",x[yindex],"],
  \"factors\": {
    \"sample\": \"",x[sampleindex],"\",
    \"cell_type\": \"",x[celltypeindex],"\"
  },
  \"poly\": []
},")
}

cat(toVitJson(dataw),file = "test_data.json")
