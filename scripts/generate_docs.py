#!/usr/bin/env python3
"""
Auto-Documentation Generator for ShopDB
Automatically generates API and model documentation from Python source code.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class DocGenerator:
    """Generate documentation from source code."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.app_dir = project_root / 'app'
        self.models_dir = self.app_dir / 'models'
        self.controllers_dir = self.app_dir / 'controllers'
        self.docs_dir = project_root / 'docs'
    
    def generate_all(self):
        """Generate all documentation."""
        print("🚀 Starting automated documentation generation...")
        print(f"📁 Project root: {self.project_root}")
        
        self.generate_model_docs()
        self.generate_api_docs()
        self.generate_quick_start()
        self.update_index()
        
        print("\n✅ Documentation generation complete!")
    
    def generate_model_docs(self):
        """Generate documentation for SQLAlchemy models."""
        print("\n📚 Generating model documentation...")
        
        models = {
            'user.py': 'User Model',
            'product.py': 'Product Model',
            'order.py': 'Order Model',
            'cart.py': 'Cart Model',
        }
        
        for filename, title in models.items():
            filepath = self.models_dir / filename
            if filepath.exists():
                doc = self._parse_model(filepath)
                self._write_model_doc(filename.replace('.py', '.md'), title, doc)
                print(f"  ✓ Generated {title}")
    
    def _parse_model(self, filepath: Path) -> Dict[str, Any]:
        """Parse model file and extract documentation."""
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract class definition
        class_match = re.search(r'class (\w+)\(.*?\):', content)
        class_name = class_match.group(1) if class_match else 'Unknown'
        
        # Extract docstring
        docstring_match = re.search(r'class.*?:\s+"""(.*?)"""', content, re.DOTALL)
        docstring = docstring_match.group(1).strip() if docstring_match else ""
        
        # Extract columns
        columns = re.findall(
            r'(\w+)\s*=\s*db\.Column\((.*?)\)',
            content
        )
        
        # Extract relationships
        relationships = re.findall(
            r'(\w+)\s*=\s*db\.relationship\((.*?)\)',
            content
        )
        
        return {
            'class_name': class_name,
            'docstring': docstring,
            'columns': columns,
            'relationships': relationships,
            'filepath': str(filepath.relative_to(self.project_root))
        }
    
    def _write_model_doc(self, filename: str, title: str, doc: Dict):
        """Write model documentation to file."""
        output_path = self.docs_dir / 'models' / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""# {title}

**Class:** `{doc['class_name']}`  
**Module:** `{doc['filepath']}`

## Overview

{doc['docstring'] or 'No description available.'}

## Database Columns

| Column | Type | Description |
|--------|------|-------------|
"""
        
        for col_name, col_type in doc['columns']:
            # Clean up column type for display
            col_type_clean = col_type.split(',')[0].strip()
            content += f"| `{col_name}` | {col_type_clean} | | \n"
        
        if doc['relationships']:
            content += "\n## Relationships\n\n"
            for rel_name, rel_target in doc['relationships']:
                content += f"- **{rel_name}**: {rel_target}\n"
        
        content += f"\n## Source Code\n\nFile: [`{doc['filepath']}`](../../{doc['filepath']})\n"
        
        with open(output_path, 'w') as f:
            f.write(content)
    
    def generate_api_docs(self):
        """Generate API documentation from blueprints."""
        print("\n📡 Generating API documentation...")
        
        api_doc = "# API Reference\n\nComplete API endpoints documentation.\n\n"
        
        blueprints = {
            'auth': 'Authentication',
            'products': 'Products',
            'orders': 'Orders',
            'cart': 'Cart',
            'main': 'General',
        }
        
        for blueprint_file, section_title in blueprints.items():
            filepath = self.controllers_dir / f'{blueprint_file}.py'
            if filepath.exists():
                routes = self._extract_routes(filepath)
                if routes:
                    api_doc += f"\n## {section_title}\n\n"
                    for route in routes:
                        api_doc += self._format_route(route)
                    print(f"  ✓ Documented {section_title} endpoints")
        
        api_doc += f"\n---\n**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        output_path = self.docs_dir / 'api' / 'endpoints.md'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(api_doc)
    
    def _extract_routes(self, filepath: Path) -> List[Dict]:
        """Extract route definitions from controller."""
        with open(filepath, 'r') as f:
            content = f.read()
        
        routes = []
        # Pattern: @blueprint.route('/path', methods=['GET', 'POST'])
        pattern = r"@blueprint\.route\('([^']+)'(?:,\s*methods=\[([^\]]+)\])?\)\s*\ndef\s+(\w+)\(.*?\):"
        
        for match in re.finditer(pattern, content):
            path = match.group(1)
            methods = match.group(2) or 'GET'
            func_name = match.group(3)
            
            # Extract docstring
            func_pattern = f"def {func_name}.*?:.*?\"\"\"(.*?)\"\"\""
            func_match = re.search(func_pattern, content[match.start():], re.DOTALL)
            docstring = func_match.group(1).strip() if func_match else ""
            
            methods_list = [m.strip().strip("'\"") for m in methods.split(',')]
            
            routes.append({
                'path': path,
                'methods': methods_list,
                'function': func_name,
                'docstring': docstring
            })
        
        return routes
    
    def _format_route(self, route: Dict) -> str:
        """Format route information as markdown."""
        methods_str = ', '.join(f"`{m}`" for m in route['methods'])
        return f"""
### {route['function']}

**Endpoint:** `{route['path']}`  
**Methods:** {methods_str}

{route['docstring'] or 'No description available.'}

"""
    
    def generate_quick_start(self):
        """Generate quick start guide."""
        print("\n⚡ Generating quick start guide...")
        
        quickstart = """# Quick Start Guide

Get ShopDB up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd advanced-database-systems-workshop
```

### 2. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3. Configure Database

```bash
# Create database
createdb shopdb
createuser shopuser --pwprompt

# Initialize schema
psql -U shopuser -d shopdb -f database/schema.sql
psql -U shopuser -d shopdb -f database/stored_procedures.sql
psql -U shopuser -d shopdb -f database/materialized_views.sql
```

### 4. Configure Application

Create `.env` file:
```ini
DATABASE_URL=postgresql://shopuser:password@localhost:5432/shopdb
SECRET_KEY=your-secret-key
FLASK_ENV=development
```

### 5. Run Application

```bash
python run.py
```

Open http://localhost:5000 in your browser.

## Common Tasks

### Create Admin User
```bash
python -c "
from app import create_app
from app.models.user import User
app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('password123')
    from app import db
    db.session.add(admin)
    db.session.commit()
"
```

### Run Tests
```bash
pytest tests/
```

### View Database
```bash
psql -U shopuser -d shopdb
```

### Generate Documentation
```bash
python scripts/generate_docs.py
```

## Project Structure

```
app/
  ├── models/         # SQLAlchemy ORM models
  ├── controllers/    # Flask Blueprint routes
  └── templates/      # Jinja2 HTML templates

database/
  ├── schema.sql              # Table definitions
  ├── stored_procedures.sql   # Database functions
  └── materialized_views.sql  # Pre-computed views

docs/
  └── ...             # Generated documentation

tests/
  └── ...             # Pytest test suite
```

## Troubleshooting

**Database Connection Error:**
```bash
# Check PostgreSQL is running
psql --version
psql -U shopuser -d shopdb -c "SELECT 1"
```

**Module Not Found:**
```bash
pip install -r requirements.txt
```

**Port Already in Use:**
```bash
# Use different port
python run.py --port 5001
```

## Next Steps

- [Full Installation Guide](../getting-started/installation.md)
- [Architecture Overview](../architecture/overview.md)
- [API Reference](../api/endpoints.md)
- [Testing Guide](../development/testing.md)

**Happy Coding! 🚀**

---
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        output_path = self.docs_dir / 'getting-started' / 'quick-start.md'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(quickstart)
        
        print("  ✓ Generated quick start guide")
    
    def update_index(self):
        """Update documentation index with generation info."""
        print("\n📝 Updating documentation index...")
        
        index_path = self.docs_dir / 'index.md'
        with open(index_path, 'r') as f:
            content = f.read()
        
        # Update last generated timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = re.sub(
            r'\*\*Last Updated:\*\*.*',
            f'**Last Updated:** Automatically generated on {timestamp}',
            content
        )
        
        with open(index_path, 'w') as f:
            f.write(content)
        
        print("  ✓ Updated documentation index")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.absolute()
    generator = DocGenerator(project_root)
    generator.generate_all()


if __name__ == '__main__':
    main()
