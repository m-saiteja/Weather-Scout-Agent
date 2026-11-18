# Weather Scout Agent

Weather Scout is an AI agent built with LangChain, LangGraph, and Groq that delivers real-time weather forecasts and web search summaries through an interactive Streamlit UI or command-line interface.

---

## Key Features

- **Fail-Fast Configuration:** Validates required environment variables on startup with helpful error messages.
- **Enterprise Observability:** Full cloud execution tracing with LangSmith and structured local logging.
- **Multi-Tier Testing & CI/CD:** Automated unit tests, agent routing tests, and benchmark behavioral evals with GitHub Actions.
- **Cloud-Native Deployment:** Production-grade **Docker** containerization and **Kubernetes** orchestration with health probes and sticky WebSocket sessions.

---

## Tech Stack

- **Runtime & Package Management:** Python 3.14+, [`uv`](https://docs.astral.sh/uv/)
- **Agent Orchestration:** LangChain, LangGraph (`create_agent`)
- **LLM Engine:** Groq (`openai/gpt-oss-20b`, temperature=0)
- **External Tools:** WeatherAPI, Tavily Search
- **User Interfaces:** Streamlit, Python CLI
- **Observability:** LangSmith (Cloud Tracing), Python standard `logging`
- **Testing & Evals:** `pytest`, `pytest-mock`, `responses`, `pytest-asyncio`
- **CI/CD:** GitHub Actions (PR Checks & Nightly Model Evals)
- **Containerization & Orchestration:** Docker, Kubernetes (`kubectl`, KinD / Docker Desktop)

---

## Project Structure

```text
Weather-Scout-Agent/
├── .github/
│   └── workflows/
│       ├── pr-check.yml            # Fast PR verification (Unit + Integration tests)
│       └── nightly-evals.yml       # Scheduled/manual benchmark behavioral evals
├── k8s/
│   ├── secret.example.yaml         # Secret manifest template for API keys
│   ├── configmap.yaml              # Non-sensitive runtime configs (LangSmith)
│   ├── deployment.yaml             # Pod specifications, replicas, health probes
│   └── service.yaml                # LoadBalancer service with WebSocket session affinity
├── src/
│   ├── __init__.py
│   ├── config.py                   # Environment loading & fail-fast validation
│   ├── prompts.py                  # System prompt templates & behavioral instructions
│   ├── agent.py                    # Agent factory with dependency injection
│   ├── cli.py                      # Interactive CLI with timing & console tracing
│   ├── ui.py                       # Streamlit web application
│   └── tools/
│       ├── __init__.py             # Public tool exports
│       ├── weather.py              # Resilient WeatherAPI tool with error handling
│       └── search.py               # Tavily search tool factory
├── tests/
│   ├── conftest.py                 # Pytest shared configuration
│   ├── unit/
│   │   └── test_weather_tool.py    # Tier 1: Deterministic offline HTTP mocking
│   ├── integration/
│   │   └── test_agent_routing.py   # Tier 2: Tool selection & parameter extraction
│   └── evals/
│       ├── golden_dataset.json     # Curated benchmark queries & assertions
│       └── test_agent_behavior.py  # Tier 3: Output quality, safety & hallucination evals
├── .dockerignore                   # Excludes .venv, .env, and caches from container images
├── Dockerfile                      # Multi-stage, uv-powered slim production container
├── .streamlit/
│   └── config.toml                 # Streamlit UI styling & theme configuration
├── main.py                         # Unified application entry point & router
├── pyproject.toml                  # Project metadata, dependencies & pytest config
└── README.md
```

---

## Getting Started

### 1. Prerequisites

- Python 3.14 or newer
- [`uv`](https://docs.astral.sh/uv/):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Docker Desktop *(for containerization and local Kubernetes)*
- API keys:
  - [Groq](https://console.groq.com/keys) (LLM inference)
  - [WeatherAPI](https://www.weatherapi.com/) (Live weather)
  - [Tavily](https://app.tavily.com/) (Web search)
  - [LangSmith](https://smith.langchain.com/) *(optional, for cloud observability)*

### 2. Installation

Clone the repository and sync dependencies:

```bash
git clone https://github.com/<your-username>/Weather-Scout-Agent.git
cd Weather-Scout-Agent
uv sync --extra dev
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# Core API Keys
GROQ_API_KEY=your_groq_api_key
WEATHER_API_KEY=your_weatherapi_key
TAVILY_API_KEY=your_tavily_api_key

# Observability (LangSmith Tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://apac.api.smith.langchain.com" # Or https://api.smith.langchain.com for US
LANGCHAIN_API_KEY="your_langsmith_api_key"
LANGCHAIN_PROJECT="weather-scout-agent"
```

---

## Running Locally

### Web UI (Streamlit)

Launch the Streamlit web application:

```bash
uv run main.py
```

Try queries like:
- *"What's the weather in Tokyo?"*
- *"What is the capital of Peru and how is the weather there?"*
- *"Find the latest developments about the James Webb telescope."*

### Command-Line Interface (CLI)

Run in interactive terminal mode:

```bash
uv run main.py --cli
```
*Tip: Type `exit`, `quit`, or `bye` to exit the session.*

---

## Containerization & Kubernetes Deployment

The project is fully containerized and includes production-ready Kubernetes manifests.

### 1. Run with Docker Standalone

Build the image using `uv` inside a slim Debian runtime:

```bash
# Build the container image
docker build -t weather-scout:v2 .

# Run the container using your local .env file
docker run -p 8501:8501 --env-file .env weather-scout:v2
```
Access the application at `http://localhost:8501`.

### 2. Deploy to Kubernetes

The Kubernetes architecture in `k8s/` follows cloud-native best practices:
- **High Availability:** 2 Pod replicas running in parallel.
- **Security:** Non-root user execution (`appuser`), secrets never committed to Git.
- **Resilience:** Liveness and readiness probes hitting Streamlit's native `/_stcore/health` endpoint.
- **Resource Management:** CPU and memory request/limit bounds.
- **WebSocket Session Affinity:** `sessionAffinity: ClientIP` in `service.yaml` keeps Streamlit's persistent WebSocket connections pinned to the correct pod.

#### Step-by-Step Kubernetes Deployment:

```bash
# 1. Create the Secret directly from your .env file (zero secrets stored in git!)
kubectl create secret generic weather-scout-secret --from-env-file=.env

# 2. Apply non-sensitive runtime configurations
kubectl apply -f k8s/configmap.yaml

# 3. Deploy the application pods (2 replicas)
kubectl apply -f k8s/deployment.yaml

# 4. Expose the deployment via the LoadBalancer service
kubectl apply -f k8s/service.yaml

# 5. Check rollout status
kubectl get pods -l app=weather-scout -w
kubectl get service weather-scout-service
```

#### Stream Live Cluster Logs:

```bash
kubectl logs -l app=weather-scout -f
```

#### Tear Down Cluster Resources:

```bash
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete secret weather-scout-secret
```

---

## Testing & Quality Strategy

The project implements a **Multi-Tier Agent Testing Pyramid** using `pytest`:

```text
               ┌────────────────────────┐
               │  3. Behavioral Evals   │  tests/evals/ (Golden Dataset)
               ├────────────────────────┤
               │  2. Agent Routing      │  tests/integration/ (Decisions)
               ├────────────────────────┤
               │  1. Tool Unit Tests    │  tests/unit/ (Mocked HTTP & Resiliency)
               └────────────────────────┘
```

### 1. Tier 1: Deterministic Tool Unit Tests (`@pytest.mark.unit`)
- **File:** `tests/unit/test_weather_tool.py`
- **What it tests:** Weather tool behavior in isolation using `responses` HTTP mocking.
- **Scenarios covered:**
  - Happy Path (HTTP 200 OK)
  - Unknown City / Client Error (HTTP 400)
  - Upstream Service Outage (HTTP 500)
  - Network Timeout & Connection Drops (`requests.exceptions.Timeout`)
- **Execution:** 100% offline, 0 API credits, runs in < 1 second.

```bash
uv run pytest -m unit -v
```

### 2. Tier 2: Agent Routing & Decision Tests (`@pytest.mark.integration`)
- **File:** `tests/integration/test_agent_routing.py`
- **What it tests:** The LLM's tool-selection intelligence using fast mock tools.
- **Scenarios covered:**
  - Weather queries trigger `weather` tool with correct location arguments.
  - Web research queries trigger `tavily_search` instead of weather.
  - Conversational chitchat (e.g. *"Hello"*) triggers zero tool calls (tool frugality).

```bash
uv run pytest -m integration -v
```

### 3. Tier 3: Output Quality & Behavioral Evals (`@pytest.mark.eval`)
- **Files:** `tests/evals/test_agent_behavior.py` & `tests/evals/golden_dataset.json`
- **What it tests:** Model responses against a curated benchmark dataset.
- **Scenarios covered:**
  - **Brevity & Conciseness:** Enforces response word limits across different categories.
  - **Information Leakage:** Ensures internal JSON, `<tool_call>`, or code blocks never leak to the user.
  - **Prompt Injection Defense:** Refuses adversarial attempts to expose system instructions or API keys.
  - **Hallucination Prevention:** Confirms the agent admits when locations are invalid rather than inventing sunny temperatures.

```bash
uv run pytest -m eval -v
```

### Running All Tests

```bash
# Run all unit and integration tests (Standard PR check):
uv run pytest -m "unit or integration" -v

# Run the complete suite:
uv run pytest -v
```

---

## CI / CD Pipelines (GitHub Actions)

The repository uses automated GitHub Actions workflows to balance developer speed, token consumption, and regression prevention:

1. **Pull Request Checks (`.github/workflows/pr-check.yml`)**
   - Triggers on every `push` and `pull_request`.
   - Runs **Unit Tests** (offline) and **Integration Tests** (routing verification).
   - Finishes in under 15 seconds, preventing broken routing or tool regressions from entering `main`.
2. **Nightly Model Evals (`.github/workflows/nightly-evals.yml`)**
   - Triggers on a nightly cron schedule (`0 0 * * *`) and manual dispatch.
   - Executes the full **Behavioral Evals benchmark suite** against Groq.
   - Monitors model quality, safety compliance, and tone drift over time.

---

## Observability & Debugging

### 1. Cloud Tracing with LangSmith
Every execution automatically streams execution trees to LangSmith when configured.
- **Waterfall View:** Visualizes the complete trajectory: `User Message` $\rightarrow$ `ChatGroq` $\rightarrow$ `weather` tool call $\rightarrow$ `ChatGroq` synthesis.
- **Autonomous Self-Correction:** Observe how the agent detects external API anomalies (e.g., location ambiguities) and self-corrects query parameters in real time.
- **Cost & Latency Tracking:** Monitor exact token consumption, model inference latency, and tool response times.

### 2. Local Structured Logging
The project uses namespaced Python logging (`logging.getLogger(__name__)`):
```text
15:30:12 | INFO    | src.tools.weather | Fetching weather data for location='Rome'
15:30:14 | INFO    | src.cli           | Agent finished response in 1.82s
```

### 3. Real-Time Terminal Tracing
The CLI interface integrates LangChain's `ConsoleCallbackHandler`, streaming live colored execution traces directly to stdout during development.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
