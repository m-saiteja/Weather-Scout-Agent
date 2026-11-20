import time
import uuid
# from langchain_core.tracers import ConsoleCallbackHandler

from src.agent import build_agent
from src.config import setup_logger
from src.guardrails import validate_input, sanitize_output
from src.rate_limiter import SlidingWindowRateLimiter

logger = setup_logger(__name__)

def run_cli():
    '''
    Run the agent in CLI mode.
    '''
    rate_limiter = SlidingWindowRateLimiter(
        max_requests=5,
        window_seconds=60,
        min_cooldown=2.0
    )
    agent = build_agent()
    thread_id = str(uuid.uuid4())
    config = {
                "configurable": {"thread_id": thread_id},
                # Enbale this if you want in console traces in real-time
                # "callbacks": [ConsoleCallbackHandler()]
            }
    print("Weather Scout (type 'exit', 'quit' or 'bye' to leave)")
    while True:
        user_input = input("Enter your question: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break

        # rate limiting
        allowed, wait = rate_limiter.check_limit(thread_id)
        if not allowed:
            print(f"Rate limited. Please wait {wait} seconds.")
            continue

        # input guradrails
        is_safe, error_msg = validate_input(user_input)
        if not is_safe:
            print(f"Guardrail Alert: {error_msg}")
            continue

        logger.info(f"User query received: '{user_input}'")
        start_time = time.time()
        agent_response = agent.invoke(
                {
                    "messages": [{
                        "role": "user", 
                        "content": user_input}],
                },
                config=config
            )
        duration = time.time() - start_time
        logger.info(f"Agent finished response in {duration:.2f}s")

        # output guardrails
        raw_response = agent_response['messages'][-1].content
        safe_response = sanitize_output(raw_response)
        print(f"Agent Response: {safe_response}")
