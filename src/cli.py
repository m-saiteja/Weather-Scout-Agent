import time
# from langchain_core.tracers import ConsoleCallbackHandler

from src.agent import build_agent
from src.config import setup_logger

logger = setup_logger(__name__)

def run_cli():
    '''
    Run the agent in CLI mode.
    '''
    agent = build_agent()
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
                # Enbale this if you want in console traces in real-time
                # config={
                #     "callbacks": [ConsoleCallbackHandler()]
                # }
            )
        duration = time.time() - start_time
        logger.info(f"Agent finished response in {duration:.2f}s")
        print(f"Agent Response: {agent_response['messages'][-1].content}")
