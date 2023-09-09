import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from collections import defaultdict
import statistics

# Load an event log (replace 'your_event_log.xes' with your log file)
log = xes_importer.apply("example.xes")

# Initialize a dictionary to store link statistics
link_statistics = defaultdict(list)
activity_names = set()

# Iterate through each trace in the event log
for trace in log:
    previous_activity = None
    for event in trace:
        activity = event["concept:name"]
        activity_names.add(activity)
        
        # Calculate waiting time between activities
        if previous_activity is not None:
            waiting_time = (event["time:timestamp"] - trace[trace.index(event) - 1]["time:timestamp"]).total_seconds()
            
            # Create a unique link identifier based on source and target activities
            link_id = f"{previous_activity} -> {activity}"
            
            # Append the waiting time to the list of waiting times for the link
            link_statistics[link_id].append(waiting_time)
        
        previous_activity = activity

# Calculate statistics for each link
link_stats_summary = {}
for link_id, waiting_times in link_statistics.items():
    link_stats_summary[link_id] = {
        "source": link_id.split(" -> ")[0],
        "target": link_id.split(" -> ")[1],
        "sum": sum(waiting_times),
        "min": min(waiting_times),
        "max": max(waiting_times),
        "median": statistics.median(waiting_times),
        "mean": statistics.mean(waiting_times),
        "std_dev": statistics.stdev(waiting_times) if len(waiting_times) > 1 else 0
    }

# Print or use the link statistics and activity names as needed
print("Link Statistics:")
print(link_stats_summary)
print("\nActivity Names:")
print(activity_names)
