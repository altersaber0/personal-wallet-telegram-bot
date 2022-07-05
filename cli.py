import os


def terminal_loop():
    """
    A loop function for recieving terminal commands,
    is a target of a Thread created by controller's main function.
    """
    while True:
        command = input("$ ")
        match command:
            case "q" | "quit" | "exit":
                print("Bot terminated. Process ended with exit code 0")

                """
                Kill the entire process. (sys.exit(0) would only kill this thread,
                which is not main)
                """
                os._exit(0)
            case _:
                print("Unknown command!")