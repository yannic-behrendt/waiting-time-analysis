from enum import Enum

SRC_ACT = "source_activity"
DEST_ACT = "destination_activity"
SRC_RSC = "source_resource"
DEST_RSC = "destination_resource"
TOTAL = "wt_total"
SIMPLE = "wt_simple"
CONTENTION = "wt_contention"
BATCHING = "wt_batching"
PRIO = "wt_prioritization"
UNAVAILABILITY = "wt_unavailability"
EXTRANEOUS = "wt_extraneous"
CASE = "case_id"
START = "start_time"
END = "end_time"


class EventLogColumns:
    START = "start_timestamp"
    COMPLETE = "time:timestamp"
    CASE = "case:concept:name"
    ACTIVITY = "concept:name"
    RESOURCE = "org:resource"


class Metrics(Enum):
    MIN = 'min'
    MAX = 'max'
    STDEV = 'stdev'
    MEDIAN = 'median'
    MEAN = 'mean'
    SUM = 'sum'


class Notions(Enum):
    SIMPLE = 'wt_simple'
    CONTROL_FLOW = 'wt_total'
