#!/usr/bin/env python3
"""
Test script for the new AI implementation with improved models and prompt engineering.
"""

import sys
import os
import time
import tempfile

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services.ai_description_generator import AIDescriptionGenerator

def test_ai_models():
    """Test the new AI implementation with different models."""
    
    print("🤖 Testing New AI Implementation")
    print("=" * 50)
    
    # Test data
    test_xsd_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="CustomerOrder">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="orderId" type="xs:string"/>
                <xs:element name="customerName" type="xs:string"/>
                <xs:element name="orderDate" type="xs:date"/>
                <xs:element name="totalAmount" type="xs:decimal"/>
                <xs:element name="items" type="OrderItems"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    <xs:complexType name="OrderItems">
        <xs:sequence>
            <xs:element name="item" type="OrderItem" maxOccurs="unbounded"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="OrderItem">
        <xs:sequence>
            <xs:element name="productId" type="xs:string"/>
            <xs:element name="quantity" type="xs:integer"/>
            <xs:element name="unitPrice" type="xs:decimal"/>
        </xs:sequence>
    </xs:complexType>
</xs:schema>"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as f:
        f.write(test_xsd_content)
        temp_file = f.name
    
    try:
        print("\n1. Testing Fast Mode (Rule-based only)")
        print("-" * 40)
        
        start_time = time.time()
        generator_fast = AIDescriptionGenerator(enable_ai=False)
        
        # Test parsing and generation
        result_fast = generator_fast.generate_descriptions(temp_file, 'xsd')
        
        fast_time = time.time() - start_time
        print(f"⏱️  Fast mode completed in {fast_time:.3f}s")
        print(f"📝 Short Description: {result_fast['short_description']}")
        print(f"📄 Detailed Description: {result_fast['detailed_description'][:200]}...")
        
        print("\n2. Testing AI Mode (with new models)")
        print("-" * 40)
        
        start_time = time.time()
        generator_ai = AIDescriptionGenerator(enable_ai=True)
        
        # Force AI initialization
        generator_ai._initialize_ai_models()
        print(f"🤖 AI model initialized: {generator_ai._ai_initialized}")
        print(f"🤖 Text generator available: {generator_ai.text_generator is not None}")
        
        # Test parsing and generation
        result_ai = generator_ai.generate_descriptions(temp_file, 'xsd')
        
        ai_time = time.time() - start_time
        print(f"⏱️  AI mode completed in {ai_time:.3f}s")
        print(f"📝 Short Description: {result_ai['short_description']}")
        print(f"📄 Detailed Description: {result_ai['detailed_description'][:200]}...")
        
        print("\n3. Performance Comparison")
        print("-" * 40)
        print(f"🚀 Fast mode: {fast_time:.3f}s")
        print(f"🤖 AI mode: {ai_time:.3f}s")
        print(f"📈 Speed difference: {ai_time/fast_time:.1f}x slower")
        
        print("\n4. Content Quality Analysis")
        print("-" * 40)
        
        # Check if AI actually generated different content
        if result_fast['detailed_description'] != result_ai['detailed_description']:
            print("✅ AI mode generated different content than rule-based")
            
            # Check if AI content looks like a prompt (the old problem)
            ai_content = result_ai['detailed_description'].lower()
            if any(prompt_indicator in ai_content for prompt_indicator in [
                'generate business description', 'integration artifact type', 
                'business description of', 'this artifact enables'
            ]):
                print("⚠️  AI content still contains prompt indicators")
            else:
                print("✅ AI content appears to be properly generated")
        else:
            print("⚠️  AI mode generated same content as rule-based (may indicate fallback)")
        
        print("\n5. Model Information")
        print("-" * 40)
        if generator_ai.text_generator:
            model_type = str(type(generator_ai.text_generator))
            print(f"🤖 Model type: {model_type}")
            if "text-generation" in model_type:
                print("✅ Using generative model (DialoGPT)")
            elif "text2text-generation" in model_type:
                print("✅ Using BART model")
            else:
                print("⚠️  Using unknown model type")
        else:
            print("❌ No AI model available")
            
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")

if __name__ == "__main__":
    test_ai_models() 