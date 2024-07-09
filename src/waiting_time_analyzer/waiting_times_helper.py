from src.waiting_time_analyzer import config
from src.waiting_time_analyzer.config import Notions, Metrics


def filter_performance_data_for_transition(data, transition):
    if transition is None:
        return data
    else:
        return data[(data[config.SRC_ACT] == transition[0]) & (data[config.DEST_ACT] == transition[1])]


def compute_waiting_times_metric(perfromance_data, metric: Metrics, notion):
    match metric:
        case Metrics.MAX.value:
            return perfromance_data[notion].max()
        case Metrics.MIN.value:
            return perfromance_data[notion].min()
        case Metrics.STDEV.value:
            return perfromance_data[notion].stdev()
        case Metrics.MEDIAN.value:
            return perfromance_data[notion].median()
        case Metrics.MEAN.value:
            return perfromance_data[notion].mean()
        case Metrics.SUM.value:
            return perfromance_data[notion].sum()
