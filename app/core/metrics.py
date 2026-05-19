from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    "research_service_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "research_service_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

RESEARCH_REQUEST_COUNT = Counter(
    "research_service_research_requests_total",
    "Total research requests",
    ["summary_mode", "evidence_strength"],
)

RESEARCH_SOURCE_COUNT = Histogram(
    "research_service_source_count",
    "Number of sources returned per research request",
)

RESEARCH_FAILED_SOURCE_COUNT = Histogram(
    "research_service_failed_source_count",
    "Number of failed sources returned per research request",
)


def render_metrics():
    return generate_latest(), CONTENT_TYPE_LATEST