import sys
import importlib.util
import os

available_commands = ["advise", "status"]

def load_module(filename, modulename):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, filename)
    spec = importlib.util.spec_from_file_location(modulename, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    if len(sys.argv) < 2:
        print(f"Usage: komon [{'|'.join(available_commands)}]")
        return

    command = sys.argv[1]

    if command == "advise":
        advise = load_module("advise.py", "advise")
        advise.run()
    elif command == "status":
        status = load_module("status.py", "status")
        status.show()
    else:
        print(f"Unknown command: {command}")
        print(f"Usage: komon [{'|'.join(available_commands)}]")

