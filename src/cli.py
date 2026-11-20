import time
import uuid
# from langchain_core.tracers import ConsoleCallbackHandler

from src.agent import build_agent
from src.config import setup_logger

logger = setup_logger(__name__)

def run_cli():
    '''
    Run the agent in CLI mode.
    '''
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
            break
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
        print(f"Agent Response: {agent_response['messages'][-1].content}")
