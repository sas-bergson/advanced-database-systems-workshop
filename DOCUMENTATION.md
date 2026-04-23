# Automated Documentation System

Guide to the automated documentation generation system for ShopDB.

## Overview

ShopDB includes a fully automated documentation system that generates and updates documentation after each commit. This system ensures documentation stays in sync with your codebase.

## Components

### 1. Documentation Generator (`scripts/generate_docs.py`)

Python script that automatically extracts and generates documentation from source code:

- **Model Documentation** - From SQLAlchemy models
- **API Documentation** - From Flask routes
- **Quick Start Guide** - Dynamic content
- **Index Updates** - Timestamps and links

```bash
python scripts/generate_docs.py
```

### 2. MkDocs Configuration (`mkdocs.yml`)

Professional documentation site configuration:

- **Material Theme** - Modern, responsive design
- **Multi-section Navigation** - Organized by topic
- **Search** - Full-text search capability
- **Minification** - Optimized assets

### 3. GitHub Actions Workflow (`.github/workflows/generate-docs.yml`)

Automated CI/CD pipeline that:

1. **Generates** - Runs doc generator on every commit
2. **Builds** - Builds MkDocs site
3. **Validates** - Checks for errors
4. **Deploys** - Publishes to GitHub Pages
5. **Updates** - Commits changes back to repository

## Workflow

### Local Development

1. **Make Changes** to code
2. **Run Generator**:
   ```bash
   python scripts/generate_docs.py
   ```
3. **Preview Locally**:
   ```bash
   mkdocs serve
   ```
4. **Review Changes** at `http://localhost:8000`
5. **Commit** your changes

### Continuous Integration (GitHub Actions)

When you push to the repository:

1. **Triggered** - Workflow runs automatically
2. **Generated** - Docs auto-generated from source
3. **Built** - MkDocs builds the site
4. **Tested** - Site structure validated
5. **Deployed** - Published to GitHub Pages
6. **Committed** - Changes committed back to branch

```yaml
# Triggers on:
on:
  push:
    branches:
      - main
      - docs/automated-documentation-system
    paths:
      - 'app/**'
      - 'database/**'
      - 'docs/**'
      - 'requirements.txt'
      - 'mkdocs.yml'
```

## Documentation Structure

```
docs/
├── index.md                      # Home page
├── getting-started/
│   ├── installation.md           # Setup guide
│   ├── configuration.md          # Config reference
│   └── quick-start.md            # 5-minute start
├── architecture/
│   ├── overview.md               # System design
│   ├── mvc-pattern.md            # MVC explanation
│   └── database-design.md        # DB principles
├── database/
│   ├── schema.md                 # Table definitions
│   ├── stored-procedures.md      # DB functions
│   ├── materialized-views.md     # Pre-computed views
│   └── indexing.md               # Performance indexes
├── api/
│   └── endpoints.md              # Auto-generated API docs
├── models/
│   ├── user.md                   # User model
│   ├── product.md                # Product model
│   ├── order.md                  # Order model
│   └── cart.md                   # Cart model
└── development/
    ├── testing.md                # Test guide
    ├── contributing.md           # Contribution guide
    └── performance.md            # Performance tuning
```

## Auto-Generated Files

These files are generated automatically from source code:

- `docs/api/endpoints.md` - From Flask route definitions
- `docs/models/*.md` - From SQLAlchemy model files
- `docs/getting-started/quick-start.md` - Dynamic content
- `docs/index.md` - Updated with latest timestamp

### What Gets Generated

**From Models:**
- Class name and location
- Database columns and types
- Model relationships
- Source code links

**From Controllers:**
- Route paths and methods
- Function names and descriptions
- Request/response documentation

## Building Documentation Locally

### Installation

```bash
pip install -r requirements.txt
mkdocs --version
```

### Development Server

```bash
mkdocs serve
# Open http://localhost:8000
```

### Build Static Site

```bash
mkdocs build
# Output in ./site/ directory
```

### Validate Build

```bash
mkdocs build --strict
# Fails on warnings
```

## Deployment

### GitHub Pages

Automatically deployed from GitHub Actions:

1. Built site goes to `gh-pages` branch
2. Published at `https://your-org.github.io/repo-name/`

### Manual Deployment

```bash
# Build and deploy
mkdocs gh-deploy

# Deploy specific site
mkdocs build
cd site
git init
git add .
git commit -m "Deploy docs"
git push origin gh-pages
```

## Customization

### Adding New Documentation Pages

1. **Create markdown file**:
   ```bash
   touch docs/new-section/new-page.md
   ```

2. **Add to navigation** in `mkdocs.yml`:
   ```yaml
   nav:
     - New Section:
         - New Page: new-section/new-page.md
   ```

3. **Rebuild**:
   ```bash
   mkdocs serve
   ```

### Customizing Theme

Edit `mkdocs.yml`:

```yaml
theme:
  name: material
  palette:
    - scheme: default
      primary: blue
      accent: orange
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - search.suggest
```

### Adding Plugins

Add to requirements.txt:

```txt
mkdocs-search-local==0.28
mkdocs-offline==2.1.0
```

Add to `mkdocs.yml`:

```yaml
plugins:
  - search
  - offline
```

## Maintenance

### Regular Tasks

```bash
# Update dependencies
pip install --upgrade mkdocs mkdocs-material

# Rebuild documentation
python scripts/generate_docs.py
mkdocs build

# Check for broken links
mkdocs build && linkchecker site/
```

### Monitoring

Check workflow status:
- GitHub Actions tab
- Workflow run history
- Failed job logs

### Troubleshooting

**Build fails:**
```bash
mkdocs build --strict --verbose
```

**Missing module:**
```bash
pip install -r requirements.txt
```

**Cache issues:**
```bash
rm -rf site/
mkdocs build
```

## Best Practices

✅ **Do:**
- Keep docs in sync with code
- Use clear, descriptive headings
- Add examples to all documentation
- Link between related pages
- Update docs before committing code
- Use proper markdown formatting
- Add timestamps for auto-generated content

❌ **Don't:**
- Manually edit auto-generated files
- Commit without running generator
- Use complex documentation structures
- Leave broken links
- Mix auto-generated and manual content

## Files to Track

Essential files for the docs system:

```
✓ mkdocs.yml                    # Config file
✓ docs/**/*.md                  # Documentation source
✓ scripts/generate_docs.py      # Generator script
✓ .github/workflows/generate-docs.yml  # CI/CD pipeline
✓ requirements.txt              # Dependencies
✗ site/                         # Build output (ignore)
```

## Next Steps

- [Installation Guide](../getting-started/installation.md)
- [Contributing Guide](../development/contributing.md)
- [MkDocs Documentation](https://www.mkdocs.org/)

---

**Last Updated:** Automatically maintained by documentation system
