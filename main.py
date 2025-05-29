# main.py

from komon.monitor import collect_resource_usage

if __name__ == "__main__":
    usage = collect_resource_usage()
    print("🧠 Komon Resource Report")
    for k, v in usage.items():
        print(f"  {k.upper()}: {v}%")
