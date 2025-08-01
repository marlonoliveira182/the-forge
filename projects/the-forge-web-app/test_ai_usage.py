import time
import tempfile
import os
from services.ai_description_generator import AIDescriptionGenerator

def test_ai_usage():
    """Test if the AI model is being triggered and working correctly."""
    
    print("🤖 Testing AI Model Usage")
    print("=" * 40)
    
    # Create generator
    generator = AIDescriptionGenerator()
    
    # Test 1: Check if AI is available
    print("\n1. Checking AI model availability...")
    if generator.text_generator is None:
        print("   ⚠️  AI model not initialized yet (lazy loading)")
    else:
        print("   ✅ AI model is available")
    
    # Test 2: Force AI initialization
    print("\n2. Testing AI model initialization...")
    start_time = time.time()
    generator._initialize_ai_models()
    init_time = time.time() - start_time
    print(f"   ✅ AI initialization completed in {init_time:.2f}s")
    
    if generator.text_generator is None:
        print("   ❌ AI model failed to initialize")
        return
    else:
        print("   ✅ AI model initialized successfully")
    
    # Test 3: Test AI generation
    print("\n3. Testing AI description generation...")
    
    # Create a simple test context
    test_context = """
    Integration artifact type: WSDL
    
    Business component 1: OrderService
    Component type: service
    Data categories: 2 port, 1 operation
    Required data elements: 2
    """
    
    start_time = time.time()
    ai_result = generator._generate_ai_description(test_context, "WSDL")
    ai_time = time.time() - start_time
    
    print(f"   ✅ AI generation completed in {ai_time:.3f}s")
    print(f"   📝 AI result: {ai_result[:100]}...")
    
    if ai_result:
        print("   ✅ AI model is working and generating content")
    else:
        print("   ❌ AI model returned empty result")
    
    # Test 4: Compare with rule-based
    print("\n4. Testing rule-based generation...")
    
    # Create a simple schema info for testing
    schema_info = {
        'file_type': 'WSDL',
        'structures': [
            {
                'name': 'OrderService',
                'type': 'service',
                'fields': [
                    {'name': 'port1', 'type': 'port', 'required': True},
                    {'name': 'operation1', 'type': 'operation', 'required': True}
                ]
            }
        ]
    }
    
    start_time = time.time()
    rule_result = generator._generate_rule_based_description(schema_info)
    rule_time = time.time() - start_time
    
    print(f"   ✅ Rule-based generation completed in {rule_time:.3f}s")
    print(f"   📝 Rule-based result length: {len(rule_result)} characters")
    
    # Test 5: Performance comparison
    print("\n5. Performance comparison...")
    print(f"   AI generation time:     {ai_time:.3f}s")
    print(f"   Rule-based time:        {rule_time:.3f}s")
    
    if ai_time > rule_time * 10:  # AI is 10x slower
        print("   ⚠️  AI is significantly slower than rule-based")
        print("   💡 Consider using rule-based as primary method")
    else:
        print("   ✅ AI performance is acceptable")
    
    # Test 6: Check if AI is actually being used in the main flow
    print("\n6. Testing full generation flow...")
    
    # Create a test WSDL file
    wsdl_content = """<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
                  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                  targetNamespace="http://example.com/order"
                  xmlns:tns="http://example.com/order">
    
    <wsdl:service name="OrderService">
        <wsdl:port name="OrderServicePort" binding="tns:OrderServiceBinding">
            <soap:address location="http://example.com/order"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(wsdl_content)
        temp_file = f.name
    
    try:
        start_time = time.time()
        result = generator.generate_descriptions(temp_file, 'wsdl')
        total_time = time.time() - start_time
        
        print(f"   ✅ Full generation completed in {total_time:.3f}s")
        print(f"   📝 Short description: {result['short_description'][:80]}...")
        print(f"   📝 Detailed description length: {len(result['detailed_description'])} characters")
        
        # Check if AI was used
        if "AI description generation completed" in str(generator.logger.handlers):
            print("   ✅ AI was triggered during generation")
        else:
            print("   ⚠️  AI may not have been triggered (check logs)")
            
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    print("\n" + "=" * 40)
    print("🎯 RECOMMENDATIONS")
    print("=" * 40)
    
    if ai_result and ai_time < 2.0:
        print("✅ AI model is working well and can be used")
    elif ai_result:
        print("⚠️  AI model works but is slow - consider optimization")
    else:
        print("❌ AI model is not working - using rule-based only")
    
    print("✅ Rule-based generation is fast and reliable")
    print("💡 Consider using rule-based as primary with AI as enhancement")

if __name__ == "__main__":
    test_ai_usage() 