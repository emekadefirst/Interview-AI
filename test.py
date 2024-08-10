import sys
print(sys.path)

try:
    import google.generativeai
    print("Successfully imported google.generativeai")
except ImportError as e:
    print(f"Failed to import: {e}")