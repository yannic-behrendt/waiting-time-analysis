import config
import statistics
from collections import defaultdict


def get_trace_durations_in_s(event_log):
    durations = {}
    for case, group in event_log.groupby(config.TRACE):
        durations[case] = int((group[config.TIMESTAMP].max() - group[config.TIMESTAMP].min()).total_seconds())

    # Print the result
    return durations


def parse_event_log(event_log):
    # Initialize a dictionary to store node and link data
    activities = defaultdict(lambda: {config.DURATION: []})
    transitions = defaultdict(lambda: {config.WAITING: [], "total_frequency": 0})

    previous_event = None
    for _, current_event in event_log.iterrows():

        current_activity = current_event[config.ACTIVITY]
        duration = 0

        '''
        The next block currently wrongly calculates waiting times. 
        TODO: Calculate Waiting times based on estimated startup timestamps
        '''
        if previous_event is not None and previous_event[config.TRACE] == current_event[config.TRACE]:
            transition = (previous_event[config.ACTIVITY], current_activity)
            # event duration, assuming the absence of start timestamps
            duration = (current_event[config.END] - previous_event[config.END]).total_seconds()
            # deprecated waiting time calculation
            waiting_time = (current_event[config.START] - previous_event[config.END]).total_seconds()

            transitions[transition]["total_frequency"] += 1
            transitions[transition][config.WAITING].append(waiting_time)

        activities[current_activity][config.DURATION].append(duration)

        previous_event = current_event

    for transition, metrics in transitions.items():
        waiting_times = transitions[transition][config.WAITING]

        transitions[transition]['sum'] = sum(waiting_times)
        transitions[transition]['min'] = min(waiting_times)
        transitions[transition]['max'] = max(waiting_times)
        transitions[transition]['median'] = statistics.median(waiting_times)
        transitions[transition]['mean'] = statistics.mean(waiting_times)
        transitions[transition]['stdev'] = statistics.stdev(waiting_times) if len(waiting_times) > 1 else 0

    epsilon = 1e-9

    mean_values = [round(value['mean']) + epsilon for value in transitions.values()]
    median_values = [round(value['median']) + epsilon for value in transitions.values()]
    max_values = [round(value['max']) + epsilon for value in transitions.values()]
    min_values = [round(value['min']) + epsilon for value in transitions.values()]
    sum_values = [round(value['sum']) + epsilon for value in transitions.values()]
    stdev_values = [round(value['stdev']) + epsilon for value in transitions.values()]

    metrics = {"mean": mean_values, "median": median_values, "max": max_values, "min": min_values, "sum": sum_values,
               "stdev": stdev_values}

    trace_durations = get_trace_durations_in_s(event_log)
    trace_count = len(event_log.groupby(config.TRACE).size())

    return dict(activities), dict(transitions), metrics, trace_durations, trace_count
