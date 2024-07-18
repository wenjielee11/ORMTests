import subprocess
import time

# Commands to be executed
commands = [
    "rm -rf migrations"
    "rm -rf prismadatabase.db",
    "prisma migrate dev --name init",
    "prisma generate",
    "python prismatest.py"
]

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(result.stderr)
        exit(1)
    else:
        print(result.stdout)

def main():
    run_command(commands[0])
    run_command(commands[1])
    start_time = time.time()
    for command in commands[2:]:
        run_command(command)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Prisma ORM benchmark time: {elapsed_time:.4f} seconds")

if __name__ == "__main__":
    main()
