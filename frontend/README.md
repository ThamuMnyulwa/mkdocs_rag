# Frontend - MkDocs Documentation Site

This directory contains the MkDocs documentation site with an embedded chat assistant.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
mkdocs serve
```

The site will be available at http://localhost:8000

## Building for Production

```bash
mkdocs build
```

This creates a `site/` directory with static HTML files ready for deployment.

## Configuration

- `mkdocs.yml` - Main configuration file
- `docs/` - Markdown documentation files
- `docs/js/chat.js` - Chat interface JavaScript

## Backend API URL

The chat interface connects to the backend API. Update the API URL in `mkdocs.yml`:

```yaml
extra:
  backend_api_url: http://localhost:8000  # Change for production
```

## GCP Deployment

The static site can be deployed to:
- Firebase Hosting
- Cloud Storage + Cloud CDN
- Cloud Run (containerized)

See the main README for deployment instructions.

