running = True

user_list = {
    "gao": "123"
}

while running:
    print("Hello, I am ccc.")
    user_name = input("Enter your username: ")
    user_password = input("Enter your password: ")
    if user_name in user_list and user_list[user_name] == user_password:
        print("Login successful!")
        print(f"Welcome, {user_name}! type 'exit' to shut down the program. Type 'help' for help.")
        while True:
            command = input("Enter a command: ")
            if command == "exit":
                print("Shutting down the program...")
                running = False
                break
            elif command == "help":
                print("Available commands:")
                print("  exit - Shut down the program")
                print("  help - Show this help message")
                print("  whoami - Display current user")
                print("  create_user - Create a new user")
            elif command == "whoami":
                print(f"You are logged in as: {user_name}")
            elif command == "create_user":
                new_username = input("Enter new username: ")
                new_password = input("Enter new password: ")
                if new_username in user_list:
                    print("Username already exists. Please choose a different username.")
                else:
                    user_list[new_username] = new_password
                    print(f"User '{new_username}' created successfully.")
            else:
                print(f"Unknown command: {command}")

    else:
        print("Invalid username or password. Please restart and re-enter your password.(Press any key to shut down.)")
        input()
        running = False