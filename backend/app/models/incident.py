from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Any


class IncidentErrorType(str, Enum):
    crash_loop_back_off = "CrashLoopBackOff"
    oom_killed = "OOMKilled"
    image_pull_backoff = "ImagePullBackOff"
    terraform_error = "TerraformError"
    aws_billing_spike = "AWSBillingSpike"
    prometheus_alert = "PrometheusAlert"
    github_action_failure = "GitHubActionFailure"
    docker_build_failure = "DockerBuildFailure"
    cloudwatch_error = "CloudWatchError"
    datadog_alert = "DatadogAlert"
    unknown = "Unknown"


class IncidentAnalyzeRequest(BaseModel):
    raw_input: str
    generate_image: bool = True


class IncidentRead(BaseModel):
    id: str
    user_id: str
    raw_input: str
    error_type: IncidentErrorType
    root_cause: str
    funny_caption: str
    suggested_fix: str
    generation_id: str | None = None
    image_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


def incident_from_doc(doc: dict[str, Any]) -> IncidentRead:
    doc["id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    if doc.get("generation_id"):
        doc["generation_id"] = str(doc["generation_id"])
    return IncidentRead(**doc)
