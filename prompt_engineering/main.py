from playground import run_simple, run_loop, run_chain

def main():
    print("\n ✨  ✨  ✨  Welcome to the Jane's Prompt Playground  ✨  ✨  ✨ ")
    print("\n ✨ Hi, Jane! Choose your mode:")
    print("\n1 - Simple (One-shot memory-assisted prompt)")
    print("2 - Loop (Generate 5 and choose what you like)")
    print("3 - Chain (Chain-of-thought poetic generation)\n")

    mode = input("Your choice (1/2/3): ").strip()

    if mode == "1":
        print("\n ✨ You Chose: Simple Memory-assisted generation ✨ ")
        run_simple()
    elif mode == "2":
        print("\n ✨ You Chose: Memory-assisted generation with Loop ✨ ")
        run_loop()
    elif mode == "3":
        print(f"\n ✨ You Chose: Chain of Thoughts with Memory-assisted generation ✨")
        run_chain()
    else:
        print(" ✨ Invalid input. Please restart and choose mode 1, 2, or 3.")

if __name__ == "__main__":
    main()
