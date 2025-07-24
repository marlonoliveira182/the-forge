from .schema_parser import SchemaParser
from .schema_field import SchemaField
from typing import List, Dict, Any
import xmlschema

class XsdSchemaParser(SchemaParser):
    def parse(self, file_path: str) -> List[SchemaField]:
        schema = xmlschema.XMLSchema(file_path)
        fields = []
        def walk(element, parent_path: str = "", level: int = 0):
            name = element.name or element.local_name or ""
            field_path = f"{parent_path}.{name}" if parent_path else name
            is_complex = element.type.is_complex() if hasattr(element.type, 'is_complex') else False
            is_array = (getattr(element, 'max_occurs', 1) not in (1, 0, None))
            cardinality = str(getattr(element, 'max_occurs', 1))
            required = getattr(element, 'min_occurs', 1) != 0
            constraints = {}
            if hasattr(element.type, 'facets'):
                for facet_name, facet in element.type.facets.items():
                    if facet_name == 'enumeration':
                        constraints['enumeration'] = [v for v in facet.enumeration]
                    elif facet_name == 'pattern':
                        constraints['pattern'] = facet.patterns[0].pattern if facet.patterns else ''
                    elif facet_name in ('minLength', 'maxLength', 'length'):
                        constraints[facet_name] = facet.value
                    elif facet_name in ('fractionDigits', 'totalDigits'):
                        constraints[facet_name] = facet.value
            description = ""
            metadata = {}
            if element.annotation is not None:
                docs = []
                if hasattr(element.annotation, 'documentation'):
                    docs = [d for d in element.annotation.documentation if hasattr(d, 'text') and d.text] or [d for d in element.annotation.documentation if isinstance(d, str) and d]
                if docs:
                    description = docs[0].text if hasattr(docs[0], 'text') else str(docs[0])
                    metadata['documentation'] = description
                if hasattr(element.annotation, 'appinfo') and element.annotation.appinfo:
                    metadata['appinfo'] = [a.text if hasattr(a, 'text') else str(a) for a in element.annotation.appinfo if a]
            description = description or ""
            metadata = metadata or {}
            levels = field_path.split('.')
            field = SchemaField(
                name=name,
                path=field_path,
                level=level,
                type=str(element.type.name) if element.type is not None else 'string',
                cardinality=cardinality,
                restrictions=constraints,
                description=description,
                parent_path=parent_path,
                is_array=is_array,
                is_complex=is_complex,
                required=required,
                metadata=metadata,
                levels=levels
            )
            fields.append(field)
            if is_complex and hasattr(element.type, 'content') and element.type.content:
                for child in element.type.content.iter_elements():
                    walk(child, field_path, level+1)
        for elem in schema.elements.values():
            walk(elem, "", 0)
        return fields 