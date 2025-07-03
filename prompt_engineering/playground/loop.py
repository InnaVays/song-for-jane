from engines import generate_loop

def run_loop():
    print("\n[Loop Mode: Generate 5 and choose what you like]")
    while True:
        prompt = input("\nEnter your poetic prompt (or type 'q' to exit): ").strip()
        if prompt.lower() in ["q", "exit"]:
            print("Goodbye, Jane.")
            break

        print("\nGenerating 5 options...\n")
        generate_loop(prompt)