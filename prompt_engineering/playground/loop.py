from engines import generate_loop

def run_loop():
    prompt = input("Enter your poetic prompt: ")
    print("\nRunning 5 memory-assisted generations. Choose what you like.")
    generate_loop(prompt)