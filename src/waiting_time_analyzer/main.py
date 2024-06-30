import logging
import BPSimpy
import pm4py
import pandas as pd

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.util import interval_lifecycle

from pandas.api.types import is_datetime64_any_dtype as is_datetime

from event_log_parser import parse_event_log
from scylla_simulation_file_generator import generate_bpmn_fom_log
from src.waiting_time_analyzer import dashboard


def get_BPSIM(event_log, file_name="bpsim.xml"):
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log)
    bpmn = pm4py.convert_to_bpmn((net, initial_marking, final_marking))

    pm4py.write_bpmn(bpmn, file_name)
    example = BPSimpy.BPSim(file_name, verbosity=None)


def get_event_log_from_csv(csv_file, separator=',', top_k=1):
    event_log = pd.read_csv(csv_file, sep=separator)
    event_log = pm4py.format_dataframe(event_log)
    event_log = dataframe_utils.convert_timestamp_columns_in_df(event_log, timest_format=pd.Timestamp.isoformat)

    print(event_log)

    event_log = pm4py.filter_variants_top_k(event_log, top_k)

    return event_log


def get_event_log_from_xes(xes_file, top_k=1):
    logging.info(f'Parsing event log: {xes_file}')
    event_log = pm4py.read_xes(xes_file)



    # filter top k
    logging.info(f'Filtering top {top_k}')
    #event_log = pm4py.filter_variants_top_k(event_log, top_k)

    event_log = log_converter.apply(event_log, variant=log_converter.Variants.TO_DATA_FRAME)
    event_log = dataframe_utils.convert_timestamp_columns_in_df(event_log, timest_format=pd.Timestamp.isoformat)

    # Make the log interval style
    return pm4py.convert_to_dataframe(interval_lifecycle.to_interval(pm4py.convert_to_event_log(event_log)))


if __name__ == '__main__':
    # import log
    # log = get_event_log_from_xes('../event_logs/'BPI_Challenge_2012.xes'')
    # log = get_event_log_from_xes('../event_logs/example.xes')
    # log = get_event_log_from_csv('../event_logs/PurchasingExample.csv')

    log = get_event_log_from_csv('../event_logs/PurchasingExample.csv', top_k=10)

    dfg, sa, ea = pm4py.discover_performance_dfg(log)
    pm4py.view_performance_dfg(dfg, sa, ea)

    activities, transitions, metrics, trace_durations, trace_count = parse_event_log(log)
    dashboard.generate_and_serve_dashboard(metrics, transitions)
