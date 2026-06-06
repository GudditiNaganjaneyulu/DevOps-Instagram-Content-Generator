import pytest
from app.services.incident_service import classify_error
from app.models.incident import IncidentErrorType


def test_classify_crash_loop():
    assert classify_error("pod is in CrashLoopBackOff state") == IncidentErrorType.crash_loop_back_off


def test_classify_oom():
    assert classify_error("container OOMKilled due to memory limit") == IncidentErrorType.oom_killed


def test_classify_terraform():
    assert classify_error("Error: creating resource on main.tf line 42") == IncidentErrorType.terraform_error


def test_classify_github_actions():
    assert classify_error("GitHub Actions workflow failed on push") == IncidentErrorType.github_action_failure


def test_classify_unknown():
    assert classify_error("some random unrelated text") == IncidentErrorType.unknown
