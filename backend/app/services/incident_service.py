import re
from datetime import datetime, timezone
from bson import ObjectId
from app.services.ai.text_engine import TextGenerationEngine
from app.services.ai.image_engine import ImageGenerationEngine
from app.models.incident import IncidentErrorType, IncidentAnalyzeRequest, IncidentRead, incident_from_doc
from app.core.logging import get_logger

logger = get_logger(__name__)

text_engine = TextGenerationEngine()
image_engine = ImageGenerationEngine()

ERROR_PATTERNS: list[tuple[re.Pattern, IncidentErrorType]] = [
    (re.compile(r"CrashLoopBackOff", re.I), IncidentErrorType.crash_loop_back_off),
    (re.compile(r"OOMKilled|OutOfMemory|memory.*limit", re.I), IncidentErrorType.oom_killed),
    (re.compile(r"ImagePullBackOff|ErrImagePull", re.I), IncidentErrorType.image_pull_backoff),
    (re.compile(r"terraform.*error|Error:.*resource|on.*\.tf\s+line", re.I), IncidentErrorType.terraform_error),
    (re.compile(r"billing.*spike|unexpected.*charge|cost.*alert", re.I), IncidentErrorType.aws_billing_spike),
    (re.compile(r"FIRING|Alertmanager|prometheus.*alert", re.I), IncidentErrorType.prometheus_alert),
    (re.compile(r"GitHub Actions.*fail|workflow.*failed|\.github/workflows", re.I), IncidentErrorType.github_action_failure),
    (re.compile(r"docker.*build.*fail|COPY.*failed|RUN.*returned.*non-zero", re.I), IncidentErrorType.docker_build_failure),
    (re.compile(r"CloudWatch|AWS.*alarm", re.I), IncidentErrorType.cloudwatch_error),
    (re.compile(r"Datadog.*alert|@datadog", re.I), IncidentErrorType.datadog_alert),
]


def classify_error(raw: str) -> IncidentErrorType:
    for pattern, error_type in ERROR_PATTERNS:
        if pattern.search(raw):
            return error_type
    return IncidentErrorType.unknown


async def analyze_and_generate(
    request: IncidentAnalyzeRequest,
    user_id: str,
    db,
) -> IncidentRead:
    error_type = classify_error(request.raw_input)
    logger.info("Incident classified", error_type=error_type)

    text_result, provider = await text_engine.generate_incident_content(
        error_type=error_type.value,
        raw_input=request.raw_input,
    )

    doc = {
        "user_id": ObjectId(user_id),
        "raw_input": request.raw_input,
        "error_type": error_type.value,
        "root_cause": text_result.get("root_cause", ""),
        "funny_caption": text_result.get("funny_caption", ""),
        "suggested_fix": text_result.get("suggested_fix", ""),
        "joke_text": text_result.get("joke_text", ""),
        "text_provider": provider,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    if request.generate_image and text_result.get("image_prompt"):
        try:
            img = await image_engine.generate_and_store(
                prompt=text_result["image_prompt"],
                folder="devops-emotions/incidents",
            )
            doc["image_url"] = img["url"]
        except Exception as e:
            logger.warning("Incident image generation failed", error=str(e))

    result = await db.incidents.insert_one(doc)
    doc["_id"] = result.inserted_id
    return incident_from_doc(doc)
