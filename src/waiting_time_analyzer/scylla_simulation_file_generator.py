import pm4py


def generate_bpmn_fom_log(event_log, bpmn_file, show=False):
    process_tree = pm4py.discover_process_tree_inductive(event_log)
    bpmn_model = pm4py.convert_to_bpmn(process_tree)

    if show:
        pm4py.view_bpmn(bpmn_model)

    pm4py.write_bpmn(bpmn_model, bpmn_file)


if __name__ == "__main__":
    log = pm4py.read_xes('../event_logs/running-example.xes')
    generate_bpmn_fom_log(log, '../scylla_input/bpmn_from_log.bpmn')
