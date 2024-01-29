from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.util import interval_lifecycle

from event_log_parser import parse_event_log
from scylla_simulation_file_generator import generate_bpmn_fom_log
from src.waiting_time_analyzer import dashboard

import pm4py
import pandas as pd


def get_event_log_from_xes(xes_file, top_k=1):
    event_log = xes_importer.apply(xes_file, variant=xes_importer.Variants.LINE_BY_LINE)

    event_log = log_converter.apply(event_log, variant=log_converter.Variants.TO_DATA_FRAME)
    event_log = dataframe_utils.convert_timestamp_columns_in_df(event_log, timest_format=pd.Timestamp.isoformat)

    # filter top k
    event_log = pm4py.filter_variants_top_k(event_log, top_k)

    # Make the log interval style
    return pm4py.convert_to_dataframe(interval_lifecycle.to_interval(pm4py.convert_to_event_log(event_log)))


if __name__ == '__main__':
    # import log
    # get_event_log_from_xes('../event_logs/'BPI_Challenge_2012.xes'')
    log = get_event_log_from_xes('../event_logs/example.xes')
    generate_bpmn_fom_log(log, '../scylla_input/xes_to_bpmn.bpmn')

    dfg, sa, ea = pm4py.discover_performance_dfg(log)
    pm4py.view_performance_dfg(dfg, sa, ea)

    activities, transitions, metrics, trace_durations, trace_count = parse_event_log(log)

    dashboard.generate_and_serve_dashboard(metrics, transitions)
