import ast
import json
from pathlib import Path


# -----------------------------
# OpenAPI metadata
# -----------------------------

OPENAPI_VERSION = "3.0.3"
API_TITLE = "Home Assistant Generated API"
API_VERSION = "1.0.0"


# -----------------------------
# Type mapping
# -----------------------------

def python_type_to_openapi(type_str: str) -> dict:
    mapping = {
        "str": {"type": "string"},
        "int": {"type": "integer"},
        "float": {"type": "number"},
        "bool": {"type": "boolean"},
        "dict": {"type": "object"},
        "list": {"type": "array"},
    }

    # Optional / Union (PEP 604: X | None)
    if "|" in type_str:
        parts = [p.strip() for p in type_str.split("|")]
        if "None" in parts:
            non_null = next(p for p in parts if p != "None")
            schema = mapping.get(non_null, {"type": "object"}).copy()
            schema["nullable"] = True
            return schema

    # list[X] / List[X]
    if type_str.startswith("list[") or type_str.startswith("List["):
        inner = type_str[type_str.find("[") + 1 : -1]
        return {
            "type": "array",
            "items": python_type_to_openapi(inner),
        }

    return mapping.get(type_str, {"type": "object"})


# -----------------------------
# AST parsing
# -----------------------------

def extract_class_fields(file_path: str, class_name: str) -> dict:
    path = Path(file_path)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=file_path)

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            fields = {}

            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    field_name = stmt.target.id
                    field_type = ast.unparse(stmt.annotation)
                    required = stmt.value is None

                    fields[field_name] = {
                        "type": field_type,
                        "required": required,
                    }

            return fields

    raise ValueError(f"Class '{class_name}' not found in {file_path}")


# -----------------------------
# OpenAPI schema conversion
# -----------------------------

def class_fields_to_openapi_schema(fields: dict) -> dict:
    schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    for name, meta in fields.items():
        schema["properties"][name] = python_type_to_openapi(meta["type"])
        if meta["required"]:
            schema["required"].append(name)

    if not schema["required"]:
        del schema["required"]

    return schema


# -----------------------------
# Main
# -----------------------------

def main():
    with open("utils/ha-entity-definitions.json", encoding="utf-8") as f:
        config = json.load(f)

    schemas = {}

    for entry in config["schemas"]:
        fields = extract_class_fields(entry["file"], entry["class"])
        schemas[entry["name"]] = class_fields_to_openapi_schema(fields)

    openapi_document = {
        "openapi": OPENAPI_VERSION,
        "info": {
            "title": API_TITLE,
            "version": API_VERSION,
            "description": "OpenAPI schemas generated from Python classes via AST parsing."
        },
        "paths": {},  # Required by OpenAPI, even if empty
        "components": {
            "schemas": schemas
        }
    }

    with open("utils/openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_document, f, indent=2)


if __name__ == "__main__":
    main()
