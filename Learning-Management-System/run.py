from app import create_app
import sys

try:
    app = create_app()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    # host='0.0.0.0' karne se ye network par visible ho jayega
    # port=5000 default hota hai, aap badal bhi sakte hain
    app.run(debug=True, host='0.0.0.0', port=5000)