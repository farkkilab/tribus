import pkg_resources
from .tribus import run_tribus, run_tribus_from_file
from .visualization import correlation_matrix, heatmap_for_median_expression, umap_vis, z_score, \
    marker_expression, marker_expression_by_cell_type, cell_type_distribution, log_zscore_normalization

__version__ = pkg_resources.get_distribution('tribus').version
