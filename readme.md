# Receipt Data Analysis System

A FastAPI-based system for processing and analyzing fuel transaction receipts, with Telegram integration for data collection and reporting. Includes a web client for SQL analysis visualization.

## Features

- **Data Extraction**: Automatically extract data from receipt images shared in Telegram groups
- **Data Analysis**: Generate SQL queries and visualizations from natural language prompts
- **Scheduled Reports**: Configure automated weekly/monthly reports via YAML configuration
- **Database Agnostic Analysis**: The analysis and visualization agent supports any MySQL or PostgreSQL database, not just fuel receipt data. Business owners can connect this system to their existing databases to gain AI-powered insights without migrating data or changing their current systems.
- **Production-Scale Support**: Handles large production databases with hundreds of tables using semantic table schema passing and few-shot learning techniques
- **Web Client Interface**: Modern dark-themed web interface for SQL analysis and visualization

## Architecture

The system follows a modified MVC architecture with:
- **Models**: Database entities (fuel transactions, vehicles, stations, etc.)
- **Controllers**: Business logic for analysis and data processing
- **Routers**: API endpoints for interacting with the system
- **Agents**: AI components for image processing, SQL generation, and visualization
- **Client**: Web interface for SQL analysis and visualization

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL
- Docker and Docker Compose (for containerized deployment)

### Environment Setup
Copy the example environment file and configure your variables:
```bash
cd server
cp .envexample .env
```

Required environment variables include:
- Database credentials
- Telegram Bot Token
- Cerebras API Key for AI services
- Telegram group chat IDs

### Server Installation

#### Local Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the application
cd app
uvicorn main:app --reload
```

#### Docker Installation
```bash
# Build and start containers
docker compose up -d

# View logs
docker compose logs -f
```

### Client Installation
The client is a static web application that can be served from any web server.

```bash
# Navigate to client directory
cd client

# Serve with a simple HTTP server for development
python -m http.server 8000
```

## Usage

### Telegram Bot
1. **Receipt Processing**: Share receipt images in the configured Telegram group
2. **Data Analysis**: Send analysis prompts to the admin Telegram group
3. **Report Scheduling**: Configure `prompt.yaml` and send to the bot via personal chat

### Web Client
1. Access the web client at the configured URL
2. Enter SQL analysis prompts in the input field
3. Select visualization type from the dropdown
4. View generated visualizations and explanations

## CI/CD Pipeline

The project includes Jenkins pipeline configurations for:
- Continuous Integration (testing and image building)
- Continuous Deployment to test and production environments

## Project Structure

Key directories:
- `server/app/agents`: AI components for data processing
- `server/app/models`: Database models
- `server/app/controllers`: Business logic
- `server/app/routers`: API endpoints
- `server/app/commands`: Scheduled tasks
- `server/app/utils`: Utility functions
- `server/app/public`: Generated reports and uploads
- `client`: Web interface for SQL analysis

