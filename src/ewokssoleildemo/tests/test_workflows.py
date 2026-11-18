from ewokscore import load_graph
from ewokscore.workflow_discovery import discover_workflows_from_modules
from ewoksutils.import_utils import import_qualname

from ewokssoleildemo.apps.xrfmap import WORKFLOW
from ewokssoleildemo.apps.xrfmap import WORKFLOW_SELECT_AREA


def test_workflows():
    workflows = discover_workflows_from_modules("ewokssoleildemo.workflows.*")
    assert sorted(workflows) == [WORKFLOW, WORKFLOW_SELECT_AREA]
    for workflow in workflows:
        graph = load_graph(workflow, representation="json_module").graph
        for _, node in graph.nodes(data=True):
            import_qualname(node["task_identifier"])
