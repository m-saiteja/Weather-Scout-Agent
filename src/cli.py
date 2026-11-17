from src.agent import build_agent

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
        agent_response = agent.invoke({
                                "messages": [{
                                    "role": "user", 
                                    "content": user_input}]
                        })
        print(f"Agent Response: {agent_response['messages'][-1].content}")
