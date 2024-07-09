import logging

import pm4py
import pandas as pd
import argparse

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.util import interval_lifecycle
from src.waiting_time_analyzer import dashboard, config
from src.waiting_time_analyzer.config import EventLogColumns


def get_lashkevich_reasons(report_csv_file, separator=','):
    df = pd.read_csv(report_csv_file, sep=separator)
    df[config.START] = pd.to_datetime(df[config.START])
    df[config.END] = pd.to_datetime(df[config.END])
    return df


def get_event_log_from_csv(csv_file, separator=','):
    event_log = pd.read_csv(csv_file, sep=separator)
    event_log = pm4py.format_dataframe(event_log, case_id=EventLogColumns.CASE)
    event_log = dataframe_utils.convert_timestamp_columns_in_df(event_log, timest_format=pd.Timestamp.isoformat)
    return event_log


def get_event_log_from_xes(xes_file):
    event_log = pm4py.read_xes(xes_file)
    event_log = log_converter.apply(event_log, variant=log_converter.Variants.TO_DATA_FRAME)
    event_log = dataframe_utils.convert_timestamp_columns_in_df(event_log, timest_format=pd.Timestamp.isoformat)

    # Make the log interval style
    return pm4py.convert_to_dataframe(interval_lifecycle.to_interval(pm4py.convert_to_event_log(event_log)))


def main(**keyword_arguments):
    if keyword_arguments['event_log'].endswith('.csv'):
        event_log = get_event_log_from_csv(keyword_arguments['event_log'])
    else:
        event_log = get_event_log_from_xes(keyword_arguments['event_log'])

    performance_analysis = get_lashkevich_reasons(keyword_arguments['performance_analysis'])
    insert_simple_wait_time(event_log, performance_analysis)

    if keyword_arguments['top_k'] is not None:
        print('filtering for top-k: ', keyword_arguments['top_k'])
        event_log = pm4py.filter_variants_top_k(event_log, keyword_arguments['top_k'])

    if keyword_arguments['case'] is not None:
        performance_analysis = performance_analysis[
            (performance_analysis[config.CASE] == keyword_arguments['case'])]
        event_log = event_log[(event_log[config.CASE] == keyword_arguments['case'])]

    dfg, sa, ea = pm4py.discover_dfg(event_log)

    dashboard.generate_and_serve_dashboard(list(dfg.keys()), performance_analysis)


def insert_simple_wait_time(event_log, performance_analysis):
    print("calculating simple waiting times...")

    for row, transition_data in performance_analysis.iterrows():
        src_act = transition_data[config.SRC_ACT]
        dest_act = transition_data[config.DEST_ACT]
        src_rsc = transition_data[config.SRC_RSC]
        dest_rsc = transition_data[config.DEST_RSC]
        case = str(transition_data[config.CASE])

        src_act = event_log[
            (event_log[EventLogColumns.ACTIVITY] == src_act) &
            (event_log[EventLogColumns.CASE] == case) &
            (event_log[EventLogColumns.RESOURCE] == src_rsc)

            ]
        dest_act = event_log[
            (event_log[EventLogColumns.ACTIVITY] == dest_act) &
            (event_log[EventLogColumns.CASE] == case) &
            (event_log[EventLogColumns.RESOURCE] == dest_rsc)
            ]

        complete_timestamp = src_act[EventLogColumns.COMPLETE]

        if len(complete_timestamp) > 1:
            complete_timestamp = complete_timestamp[(complete_timestamp == transition_data[config.END])]

        start_timestamp = dest_act[EventLogColumns.START]

        if len(start_timestamp) > 1:
            start_indices = start_timestamp.index
            complete_index = complete_timestamp.index[0]

            mask = (start_indices - complete_index == 1)
            start_timestamp_index = start_indices[mask]

            if len(start_timestamp_index) == 1:
                # event directly follows
                start_timestamp = start_timestamp[start_timestamp_index]
            else:
                # event does not directly follow
                start_indices = start_indices[start_indices != complete_index]
                closest_idx = min(start_indices, key=lambda idx: abs(idx - complete_index))
                start_timestamp_index = start_indices[(start_indices == closest_idx)]
                start_timestamp = start_timestamp[start_timestamp_index]

        assert pd.notna(start_timestamp).all()
        assert pd.notna(complete_timestamp).all()
        assert len(start_timestamp) == len(complete_timestamp) == 1

        start_timestamp = start_timestamp.iloc[0]
        complete_timestamp = complete_timestamp.iloc[0]

        assert (start_timestamp >= complete_timestamp)

        waiting_time = (start_timestamp - complete_timestamp).total_seconds()

        performance_analysis.loc[row, config.SIMPLE] = waiting_time

    performance_analysis[config.SIMPLE] = performance_analysis[config.SIMPLE].replace(0.0, 1e-10)
    return performance_analysis


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='test')

    parser.add_argument('--event_log', type=str, help='Path to the eventlog file in xes or csv')
    parser.add_argument('--performance_analysis', type=str, help='Path to the waiting time analysis')
    parser.add_argument('--top_k', type=int, default=None, help='filter the event log by top k most frequent paths')
    parser.add_argument('--case', type=str, default=None, help='filter the data by a specific case')

    args = parser.parse_args()
    kwargs = vars(args)
    main(**kwargs)
