# Weather Scout Agent

Weather Scout is a small AI agent that answers questions using current weather
data and web search. Ask about a city's conditions, look up information online,
or combine both in one question.

The Streamlit interface uses a sky-inspired light/dark theme and presents the
agent's weather and web-search capabilities alongside a question form. A
command-line interface is also available.

## Tech stack

- **Python 3.14+** — application runtime
- **Streamlit** — web UI and light/dark theme
- **LangChain** — agent orchestration and tool integration
- **Groq** (`openai/gpt-oss-20b`) — language model for composing answers
- **Tavily** — web search
- **WeatherAPI** — current weather data
- **python-dotenv** — local environment-variable loading
- **Requests** and **Certifi** — weather API requests and trusted certificates
- **uv** — dependency management and project execution

## Requirements

- Python 3.14 or newer
- API keys for [Groq](https://console.groq.com/keys),
  [Tavily](https://app.tavily.com/home), and
  [WeatherAPI](https://www.weatherapi.com/)
- [uv](https://docs.astral.sh/uv/) for dependency management (recommended)

## Setup

1. Clone the repository and change into its directory.
2. Install the project dependencies:

   ```bash
   uv sync
   ```

3. Create a `.env` file in the project root and add your API keys:

   ```dotenv
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   WEATHER_API_KEY=your_weatherapi_key
   ```

Keep the `.env` file private; do not commit API keys to version control.

## Run the app

Start the Streamlit interface:

```bash
uv run main.py
```

The app opens in your browser. Enter a question such as:

- “What’s the weather in Tokyo?”
- “What’s the capital of India and its current weather?”
- “Find a few things to do in Vancouver and tell me the forecast.”

Weather questions use WeatherAPI's current-conditions endpoint. Web searches
use Tavily, and Groq's `openai/gpt-oss-20b` model composes a concise answer.

To use the command-line interface instead:

```bash
uv run main.py --cli
```

Type `exit`, `quit`, or `bye` to leave the CLI.

## Configuration

The Streamlit theme is configured in `.streamlit/config.toml`. It includes
weather-inspired teal accents and coordinated light and dark color palettes.

Dependencies and the supported Python version are declared in `pyproject.toml`.