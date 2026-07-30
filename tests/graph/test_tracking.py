from types import MappingProxyType

from backend.app.graph.tracking import (
    NODE_TO_PROGRESS,
    NODE_TO_STAGE,
)
from backend.app.models.enums import TaskStage


def test_node_to_stage():
    assert NODE_TO_STAGE == {
        "planner": TaskStage.PLANNING,
        "query_generator": TaskStage.QUERY_GENERATION,
        "web_search": TaskStage.WEB_SEARCH,
        "arxiv_search": TaskStage.ARXIV_SEARCH,
        "merge_documents": TaskStage.MERGING,
        "writer": TaskStage.WRITING_REPORT,
        "summarizer": TaskStage.SUMMARIZING,
    }


def test_node_to_progress():
    assert NODE_TO_PROGRESS == {
        "planner": 10,
        "query_generator": 20,
        "web_search": 35,
        "arxiv_search": 50,
        "merge_documents": 65,
        "writer": 85,
        "summarizer": 95,
    }


def test_stage_and_progress_nodes_match():
    assert set(NODE_TO_STAGE) == set(NODE_TO_PROGRESS)


def test_all_progress_values_are_valid():
    assert all(
        0 <= progress <= 100
        for progress in NODE_TO_PROGRESS.values()
    )


def test_progress_values_are_increasing():
    progress_values = list(NODE_TO_PROGRESS.values())

    assert progress_values == sorted(progress_values)
    assert len(progress_values) == len(set(progress_values))


def test_mappings_are_mapping_proxy():
    assert isinstance(NODE_TO_STAGE, MappingProxyType)
    assert isinstance(NODE_TO_PROGRESS, MappingProxyType)


def test_mappings_are_immutable():
    try:
        NODE_TO_STAGE["planner"] = TaskStage.FAILED
        assert False, "NODE_TO_STAGE should be immutable"
    except TypeError:
        pass

    try:
        NODE_TO_PROGRESS["planner"] = 999
        assert False, "NODE_TO_PROGRESS should be immutable"
    except TypeError:
        pass