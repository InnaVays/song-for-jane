from engines import generate_loop

def run_loop():
    while True:
        
        prompt = input("\n ✨ Enter your poetic prompt (or type 'q' or 'exit'): ").strip()
        print("Jane says: "+prompt)
        if prompt.lower() in ["q", "exit"]:
            print("✨ Goodbye, Jane.")
            break

        if prompt == '':
            print("\n ✨ You didn't give a topic, Jane! Let me surprise you! ")
            prompt = 'Hippopotamus meets a badger'

        print("\n Generating 3 options..." )
        print("\n ✨ Look, what I've written : \n" )

        generate_loop(prompt)

# False pretenses are dinner invitations that turn into unpaid babysitting shifts.