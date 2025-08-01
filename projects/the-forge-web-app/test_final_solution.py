#!/usr/bin/env python3
"""
Final test to verify the complete AI description generator solution.
"""

import sys
import os
import tempfile
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ai_description_generator import AIDescriptionGenerator

def test_final_solution():
    """Test the final AI description generator solution with multiple file types."""
    
    print("🎯 Testing Final AI Description Generator Solution")
    print("=" * 60)
    
    # Test cases with different file types
    test_cases = [
        {
            'name': 'XSD - Customer Order',
            'type': 'XSD',
            'content': '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="CustomerOrder">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="customerId" type="xs:string" minOccurs="1" maxOccurs="1"/>
                <xs:element name="orderDate" type="xs:date" minOccurs="1" maxOccurs="1"/>
                <xs:element name="totalAmount" type="xs:decimal" minOccurs="1" maxOccurs="1"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
        },
        {
            'name': 'JSON Schema - Product Catalog',
            'type': 'JSON Schema',
            'content': '''{
  "type": "object",
  "properties": {
    "productId": {"type": "string"},
    "productName": {"type": "string"},
    "price": {"type": "number"},
    "category": {"type": "string"},
    "inStock": {"type": "boolean"}
  },
  "required": ["productId", "productName", "price"]
}'''
        },
        {
            'name': 'JSON - User Profile',
            'type': 'JSON',
            'content': '''{
  "userId": "12345",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "age": 30,
  "isActive": true
}'''
        }
    ]
    
    # Initialize the AI description generator
    print("📋 Initializing AI Description Generator...")
    ai_generator = AIDescriptionGenerator(enable_ai=True)
    
    total_time = 0
    successful_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*20} Test {i}: {test_case['name']} {'='*20}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{test_case["type"].lower()}', delete=False) as f:
            f.write(test_case['content'])
            temp_file_path = f.name
        
        try:
            # Generate descriptions
            start_time = time.time()
            descriptions = ai_generator.generate_descriptions(temp_file_path, test_case['type'])
            generation_time = time.time() - start_time
            total_time += generation_time
            
            print(f"⏱️  Generation time: {generation_time:.2f}s")
            
            # Display results
            print(f"\n📋 SHORT DESCRIPTION:")
            print("-" * 30)
            short_desc = descriptions.get('short_description', 'No short description generated')
            print(short_desc)
            
            print(f"\n📋 DETAILED DESCRIPTION:")
            print("-" * 30)
            detailed_desc = descriptions.get('detailed_description', 'No detailed description generated')
            print(detailed_desc)
            
            # Quality checks
            print(f"\n🔍 Quality Analysis:")
            print(f"Short description length: {len(short_desc)} characters")
            print(f"Detailed description length: {len(detailed_desc)} characters")
            
            # Check if descriptions are business-friendly
            business_terms = ['business', 'integration', 'system', 'data', 'information', 'process']
            has_business_focus = any(term in detailed_desc.lower() for term in business_terms)
            
            if has_business_focus and len(detailed_desc) > 100:
                print("✅ High-quality business-focused description")
                successful_tests += 1
            else:
                print("⚠️  Description may need improvement")
                
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Total tests: {len(test_cases)}")
    print(f"Successful tests: {successful_tests}")
    print(f"Success rate: {(successful_tests/len(test_cases)*100):.1f}%")
    print(f"Total generation time: {total_time:.2f}s")
    print(f"Average time per test: {(total_time/len(test_cases)):.2f}s")
    
    if successful_tests == len(test_cases):
        print("\n🎉 All tests passed! The solution is working correctly.")
    else:
        print(f"\n⚠️  {len(test_cases) - successful_tests} tests had issues.")

if __name__ == "__main__":
    test_final_solution() 