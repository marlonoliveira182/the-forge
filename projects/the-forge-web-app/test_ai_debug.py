#!/usr/bin/env python3
"""
Debug script to see what the AI is actually generating before filtering.
"""

import sys
import os
import tempfile

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ai_description_generator import AIDescriptionGenerator

def test_ai_raw_output():
    """Test the AI description generator and see the raw output before filtering."""
    
    print("🔍 Debugging AI Raw Output")
    print("=" * 60)
    
    # Create a sample XSD content for testing
    sample_xsd = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="CustomerOrder">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="customerId" type="xs:string" minOccurs="1" maxOccurs="1"/>
                <xs:element name="orderDate" type="xs:date" minOccurs="1" maxOccurs="1"/>
                <xs:element name="orderItems" type="OrderItems" minOccurs="1" maxOccurs="1"/>
                <xs:element name="totalAmount" type="xs:decimal" minOccurs="1" maxOccurs="1"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as f:
        f.write(sample_xsd)
        temp_file_path = f.name
    
    try:
        # Initialize the AI description generator with AI enabled
        print("📋 Initializing AI Description Generator...")
        ai_generator = AIDescriptionGenerator(enable_ai=True)
        
        # Force initialization of AI models
        print("🤖 Initializing AI models...")
        ai_generator._initialize_ai_models()
        
        # Parse the schema to get context
        schema_info = ai_generator._parse_schema_file(temp_file_path, 'XSD')
        context = ai_generator._build_ai_context(schema_info)
        
        print(f"\n📋 Context being sent to AI:")
        print("-" * 30)
        print(context)
        
        print(f"\n🤖 Testing AI generation directly...")
        
        # Test the AI generation directly
        if ai_generator.text_generator:
            print(f"✅ AI model available: {type(ai_generator.text_generator)}")
            
            # Use a much simpler, more direct prompt that works better with available models
            simple_prompt = f"Describe what this XSD file does for business in 5-10 sentences. Focus on functional purpose and business value: {context}"
            
            print(f"\n📝 Sending prompt to AI...")
            print(f"Prompt length: {len(simple_prompt)} characters")
            print(f"Prompt: {simple_prompt}")
            
            if "text-generation" in str(type(ai_generator.text_generator)):
                result = ai_generator.text_generator(simple_prompt, max_length=200, min_length=100, do_sample=True, temperature=0.7, truncation=True)
                generated_text = result[0]['generated_text']
                # Extract only the generated part (remove the prompt)
                description = generated_text[len(simple_prompt):].strip()
                
            elif "text2text-generation" in str(type(ai_generator.text_generator)):
                result = ai_generator.text_generator(simple_prompt, max_length=200, min_length=100, do_sample=True, temperature=0.7)
                description = result[0]['generated_text']
            else:
                result = ai_generator.text_generator(simple_prompt, max_length=200, min_length=100, do_sample=True, temperature=0.7)
                description = result[0]['generated_text'] if 'generated_text' in result[0] else result[0].get('summary_text', '')
            
            print(f"\n🤖 RAW AI OUTPUT:")
            print("=" * 60)
            print(description)
            print("=" * 60)
            
            # Check for problematic indicators with relaxed validation
            problematic_indicators = [
                'api gateway json api gateway',  # Repetitive gibberish
                'xs:string xs:date xs:decimal',  # Technical jargon
                'integration artifact type',      # Context repetition
                'business component component type'  # Context repetition
            ]
            
            has_problematic_content = any(indicator in description.lower() for indicator in problematic_indicators)
            
            print(f"\n🔍 Content Analysis:")
            print(f"Length: {len(description)} characters")
            print(f"Has problematic content: {has_problematic_content}")
            
            if has_problematic_content:
                print("❌ Content would be filtered out as problematic")
            else:
                print("✅ Content would pass validation")
                
        else:
            print("❌ AI model not available")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

if __name__ == "__main__":
    test_ai_raw_output() 