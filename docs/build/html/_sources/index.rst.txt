.. tribus_documentation documentation master file, created by
   sphinx-quickstart on Mon Jun  5 10:40:23 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TRIBUS's documentation!
================================================

Tribus is a python modul for cell-type annotation of multiplexed-image data.
Tribus is based on semi-supervised learning for which no training data is needed.
Tribus makes cell-type calling fast and reproducible.
Furthermore various functions are built-in for visualization to better understand the
input data and to benchmark the results.

Tribus is using Self-Organizing Map (SOM) in the background to cluster the data and
then it assigns to each cluster a cell-type based on previous-knowledge, which is an input of Tribus.
Tribus can be used in multiple level, first making high-level annotation, and then divide the first-level
cell types into more specific cell types.

.. toctree::
   :maxdepth: 2
   :caption: Tutorial

   tutorial

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   tribus


