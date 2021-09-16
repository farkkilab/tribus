#!/usr/bin/env Rscript
args = commandArgs(TRUE)
if(length(args)==2) {
  print("Given two arguments, producing a report containing a comparison")
  rmarkdown::render('report.Rmd',params = list(oldpath = args[1], newpath = args[2], comparison=TRUE))
} else if (length(args)==1) {
  print("Given one argument, producing a report without comparison")
  rmarkdown::render('report.Rmd',params = list(oldpath = args[1], newpath = "", comparison=FALSE))
} else {
  print("Given either too few or too many arguments. Please provide one or two filepaths.")
}

