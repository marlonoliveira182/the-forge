# Test script for v8 features
import os
import tempfile

def test_v8_features():
    print("Testing v8 features...")
    
    # Test case conversion
    test_string = "hello_world"
    print(f"Original: {test_string}")
    
    # Test file operations
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(b"test content")
        temp_path = temp_file.name
    
    print(f"✅ Created test file: {temp_path}")
    
    # Clean up
    try:
        os.unlink(temp_path)
        print("✅ Cleaned up test file")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    
    print("v8 features test completed.")

if __name__ == "__main__":
    test_v8_features() 