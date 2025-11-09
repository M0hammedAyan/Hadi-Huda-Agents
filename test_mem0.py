from dotenv import load_dotenv
from mem0 import MemoryClient
import logging
import json

load_dotenv()
user_name = 'Ayan'
mem0 = MemoryClient()

def add_memory():
    messages_formatted = [
        {"role": "user", "content": "I really like Linkin Park."},
        {"role": "assistant", "content": "That is a good choice."},
        {"role": "user", "content": "I think so too."},
        {"role": "assistant", "content": "What is your favorite song by them?"},
    ]
    mem0.add(messages_formatted, user_id=user_name)

def get_memory_by_query():
    query = f"What are {user_name}'s preferences?"
    results = mem0.search(query, user_id=user_name)

    memories = [
        {"memory": r["memory"], "updated_at": r["updated_at"]}
        for r in results
    ]
    print(f"Memories: {json.dumps(memories, indent=2)}")
    return memories

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    add_memory()
    get_memory_by_query()
