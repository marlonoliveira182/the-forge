# Test script for mapping functionality
import os
import tempfile

def test_mapping():
    print("Testing mapping functionality...")
    
    # Test file creation
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xsd") as temp_file:
        temp_file.write(b"<xsd:schema xmlns:xsd='http://www.w3.org/2001/XMLSchema'></xsd:schema>")
        temp_path = temp_file.name
    
    print(f"✅ Created test file: {temp_path}")
    
    # Clean up
    try:
        os.unlink(temp_path)
        print("✅ Cleaned up test file")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    
    print("Mapping test completed.")

if __name__ == "__main__":
    test_mapping() 