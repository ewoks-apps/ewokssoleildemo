from ewokscore import load_graph
from ewokscore.workflow_discovery import discover_workflows_from_modules
from ewoksutils.import_utils import import_qualname


def test_workflows():
    workflows = discover_workflows_from_modules("ewokssoleildemo.workflows.*")
    assert sorted(workflows) == [
        "ewokssoleildemo.workflows.xrfmap_flyscan",
        "ewokssoleildemo.workflows.xrfmap_flyscan_select_area",
    ]
    for workflow in workflows:
        graph = load_graph(workflow, representation="json_module").graph
        for _, node in graph.nodes(data=True):
            import_qualname(node["task_identifier"])
