from llm_integration import generate_response

if __name__ == "__main__":
    while True:
        msg = input()
        if msg.lower() in ["exit", "quit"]:
            break
        reply = generate_response(msg)
        print(reply)
