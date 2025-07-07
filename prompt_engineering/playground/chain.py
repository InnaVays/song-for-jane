from engines import generate_chain
from memory import save_in_memory

def run_chain():

    while True:
        prompt = input("\n ✨ Enter the topic, you want to write about (or type 'q' or 'exit'): ").strip()
        print("Jane says: "+prompt)
        
        if prompt.lower() in ["q", "exit"]:
            print(" ✨ Goodbye, Jane.")
            break

        if prompt == '':
            print("\n ✨ You didn't give a topic, Jane! Let me surprise you! ")
            prompt = 'Hippopotamus meets a badger'

        output = generate_chain(prompt)