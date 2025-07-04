from engines import generate_chain
from memory import save_in_memory

def run_chain():
    print("\n Chain Mode: Guided emotional/metaphoric writing ")
    print("\n Hi, Jane! ")
    while True:
        topic = input("\n What do you want to write about? (or type 'q' to exit): ").strip()
        if topic.lower() in ["q", "exit"]:
            print("Goodbye, Jane.")
            break

        output = generate_chain(topic)