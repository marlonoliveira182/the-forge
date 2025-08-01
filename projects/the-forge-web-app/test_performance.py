import time
import tempfile
import os
from services.ai_description_generator import AIDescriptionGenerator

def test_performance():
    """Test the performance of AI description generation."""
    
    # Sample WSDL content for testing
    wsdl_content = """<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
                  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                  targetNamespace="http://example.com/order"
                  xmlns:tns="http://example.com/order">
    
    <wsdl:message name="ProcessOrderRequest">
        <wsdl:part name="body" element="tns:ProcessOrder"/>
    </wsdl:message>
    
    <wsdl:message name="ProcessOrderResponse">
        <wsdl:part name="body" element="tns:ProcessOrderResponse"/>
    </wsdl:message>
    
    <wsdl:portType name="OrderService">
        <wsdl:operation name="ProcessOrder">
            <wsdl:input message="tns:ProcessOrderRequest"/>
            <wsdl:output message="tns:ProcessOrderResponse"/>
        </wsdl:operation>
    </wsdl:portType>
    
    <wsdl:binding name="OrderServiceBinding" type="tns:OrderService">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="ProcessOrder">
            <soap:operation soapAction="http://example.com/order/ProcessOrder"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    
    <wsdl:service name="OrderService">
        <wsdl:port name="OrderServicePort" binding="tns:OrderServiceBinding">
            <soap:address location="http://example.com/order"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>"""
    
    print("🔍 Performance Test for AI Description Generator")
    print("=" * 50)
    
    # Test 1: Initialization time
    print("\n1. Testing initialization time...")
    start_time = time.time()
    generator = AIDescriptionGenerator()
    init_time = time.time() - start_time
    print(f"   ✅ Initialization completed in {init_time:.2f} seconds")
    
    # Test 2: File parsing time
    print("\n2. Testing file parsing time...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(wsdl_content)
        temp_file = f.name
    
    try:
        start_time = time.time()
        schema_info = generator._parse_schema_file(temp_file, 'wsdl')
        parse_time = time.time() - start_time
        print(f"   ✅ File parsing completed in {parse_time:.2f} seconds")
        print(f"   📊 Parsed {schema_info.get('total_structures', 0)} structures")
        
        # Test 3: Short description generation
        print("\n3. Testing short description generation...")
        start_time = time.time()
        short_desc = generator._generate_short_description(schema_info)
        short_time = time.time() - start_time
        print(f"   ✅ Short description generated in {short_time:.2f} seconds")
        print(f"   📝 Short description: {short_desc[:100]}...")
        
        # Test 4: Detailed description generation
        print("\n4. Testing detailed description generation...")
        start_time = time.time()
        detailed_desc = generator._generate_detailed_description(schema_info)
        detailed_time = time.time() - start_time
        print(f"   ✅ Detailed description generated in {detailed_time:.2f} seconds")
        print(f"   📝 Detailed description length: {len(detailed_desc)} characters")
        
        # Test 5: Full generation process
        print("\n5. Testing full generation process...")
        start_time = time.time()
        result = generator.generate_descriptions(temp_file, 'wsdl')
        full_time = time.time() - start_time
        print(f"   ✅ Full generation completed in {full_time:.2f} seconds")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"Initialization:     {init_time:.2f}s")
        print(f"File parsing:       {parse_time:.2f}s")
        print(f"Short description:  {short_time:.2f}s")
        print(f"Detailed description: {detailed_time:.2f}s")
        print(f"Total generation:   {full_time:.2f}s")
        print(f"Overhead:           {full_time - (parse_time + short_time + detailed_time):.2f}s")
        
        # Performance analysis
        if full_time > 5.0:
            print("\n⚠️  PERFORMANCE ISSUE DETECTED")
            print("The generation is taking too long. Recommendations:")
            if init_time > 2.0:
                print("   - AI model initialization is slow, consider lazy loading")
            if parse_time > 1.0:
                print("   - File parsing is slow, consider optimization")
            if detailed_time > 2.0:
                print("   - Detailed description generation is slow, consider caching")
        else:
            print("\n✅ PERFORMANCE IS ACCEPTABLE")
            print("Generation time is within acceptable limits.")
            
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    test_performance() 