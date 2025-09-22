# 2025 GitHub Copilot Workshop - Python Flask Application

## Overview
This is a Python Flask application with basic infrastructure setup including database integration, health monitoring, and time provider abstraction.

## Features
- Flask application with factory pattern
- Blueprint-based modular architecture
- SQLite database integration
- Health check endpoint (`/health`)
- Time provider abstraction for testable time operations
- Environment-based configuration

## Installation and Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd 2025-09-22-Github-Copilot-Workshop-Python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

The application will start on `http://localhost:5000` by default.

### Configuration

The application uses environment-based configuration:

- **Development** (default): Debug mode enabled, SQLite database
- **Production**: Debug mode disabled, production settings
- **Testing**: In-memory SQLite database for testing

Set the `FLASK_ENV` environment variable to change configurations:
```bash
export FLASK_ENV=production
python main.py
```

### Available Endpoints

- **Health Check**: `GET /health`
  - Returns service status and timestamp
  - Used for monitoring and health checks

### Database

The application uses SQLite database with automatic table creation on startup. The database file (`app.db`) will be created in the project root directory.

### Time Provider

The application includes a time provider abstraction (`time_provider.py`) that allows for:
- Real time operations in production
- Mock time operations for testing
- Consistent time handling across the application

## Development

To run in development mode:
```bash
export FLASK_ENV=development
python main.py
```

The server will run with debug mode enabled and auto-reload on code changes.

## Existing Code

This repository also contains existing Python code for a kitchen game management system:
- `deliverManager.py` - Game delivery management system
- `point.py` - Point system (placeholder)

These files remain functional and can be used independently of the Flask web application.

## Workshop Reference
ワークショップの手順：https://moulongzhang.github.io/2025-Github-Copilot-Workshop/github-copilot-workshop/#0
