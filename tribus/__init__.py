import pkg_resources
from tribus.tribus import run_tribus, run_tribus_from_file
from tribus.visualization import correlation_matrix, heatmap_for_median_expression, umap_vis, z_score

__version__ = pkg_resources.get_distribution('tribus').version
