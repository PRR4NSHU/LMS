from app import create_app
import sys

try:
    print("--- Checking App Factory ---")
    app = create_app()
    print("--- App Created Successfully ---")
except Exception as e:
    print(f"--- Error during App Creation: {e} ---")
    sys.exit(1)

if __name__ == "__main__":
    try:
        print("--- Starting Flask Server ---")
        app.run(debug=True)
    except Exception as e:
        print(f"--- Server Crash Error: {e} ---")