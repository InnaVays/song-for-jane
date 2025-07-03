from engines import generate_with_memory, generate_loop, chain_of_thought_prompt

def main():
    print("Welcome to the Jane Prompt Playground 🎤")
    print("Choose your mode:")
    print("1 - Simple (One-shot memory-assisted prompt)")
    print("2 - Loop (Generate 5 and choose what you like)")
    print("3 - Chain (Chain-of-thought poetic generation)")

    mode = input("Your choice (1/2/3): ").strip()

    if mode == "1":
        from scripts.simple_mode import run_simple
        run_simple()
    elif mode == "2":
        from scripts.loop_mode import run_loop
        run_loop()
    elif mode == "3":
        from scripts.chain_mode import run_chain
        run_chain()
    else:
        print("Invalid input. Please restart and choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
