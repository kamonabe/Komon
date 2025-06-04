# komon/cli.py
import sys
import importlib.util
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: komon [advise]")
        return

    command = sys.argv[1]

    if command == "advise":
        # advise.py はルート直下なので、パスを明示してインポート
        advise_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "advise.py")
        spec = importlib.util.spec_from_file_location("advise", advise_path)
        advise = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(advise)
        advise.run()
    elif command == "status":
        # status.py はルート直下なので、パスを明示してインポート
        status_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "status.py")
        spec = importlib.util.spec_from_file_location("status", status_path)
        status = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(status)
        status.show()
    else:
        print(f"Unknown command: {command}")
        print("Usage: komon [advise]")

