import sys
import requests
import uuid

API_URL = "http://localhost:8000/agent/ask"

def main():
    print("=========================================")
    print("🤖 Welcome to the TeamFlow CLI Chatbot!")
    print("Type 'exit' or 'quit' to stop.")
    print("=========================================")
    
    # Generate a unique thread ID for this chat session to maintain conversational memory
    thread_id = str(uuid.uuid4())
    print(f"[Session Thread ID: {thread_id}]")
    print("Connecting to backend on http://localhost:8000...")
    
    while True:
        try:
            question = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
            
        if question.lower().strip() in ["exit", "quit"]:
            break
            
        if not question.strip():
            continue
            
        payload = {
            "question": question,
            "thread_id": thread_id
        }
        
        try:
            # Hit the FastAPI POST /agent/ask endpoint
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            print(f"\nTeamFlow Agent: {data['answer']}")
            
            # Print sources if any were returned (mostly for RAG path)
            if data.get("sources"):
                print(f"🔗 [Sources: {', '.join(data['sources'])}]")
                
        except requests.exceptions.ConnectionError:
            print("\n❌ [Error] Could not connect to the server. Make sure your FastAPI backend is running on http://localhost:8000")
        except requests.exceptions.HTTPError as e:
            print(f"\n❌ [Error] The server returned an error: {e}")
        except Exception as e:
            print(f"\n❌ [Error] Something went wrong: {e}")

if __name__ == "__main__":
    main()
