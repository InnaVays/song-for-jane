from engines import generate_multiple

def run_multiple():
    while True:
        
        prompt = input("\n ✨ Enter your poetic prompt (or type 'q' or 'exit'): ").strip()
        print("Jane says: "+prompt)
        if prompt.lower() in ["q", "exit"]:
            print("✨ Goodbye, Jane.")
            break

        if prompt == '':
            print("\n ✨ You didn't give a topic, Jane! Let me surprise you! ")
            prompt = 'Hippopotamus meets a badger'

        generate_loop(prompt, num_attempts=3)

# False pretenses are dinner invitations that turn into unpaid babysitting shifts.