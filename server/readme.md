# Receipt Data Analysis System

A FastAPI-based system for processing and analyzing fuel transaction receipts, with Telegram integration for data collection and reporting.

## Features

- **Data Extraction**: Automatically extract data from receipt images shared in Telegram groups
- **Data Analysis**: Generate SQL queries and visualizations from natural language prompts
- **Scheduled Reports**: Configure automated weekly/monthly reports via YAML configuration
- **Database Agnostic Analysis**: The analysis and visualization agent supports any MySQL or PostgreSQL database, not just fuel receipt data. Business owners can connect this system to their existing databases to gain AI-powered insights without migrating data or changing their current systems.
- **Production-Scale Support**: Handles large production databases with hundreds of tables using semantic table schema passing and few-shot learning techniques

## Architecture

The system follows a modified MVC architecture with:
- **Models**: Database entities (fuel transactions, vehicles, stations, etc.)
- **Controllers**: Business logic for analysis and data processing
- **Routers**: API endpoints for interacting with the system
- **Agents**: AI components for image processing, SQL generation, and visualization

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL
- Docker and Docker Compose (for containerized deployment)

### Environment Setup
Copy the example environment file and configure your variables:
```bash
cp .envexample .env
```

Required environment variables include:
- Database credentials
- Telegram Bot Token
- Cerebras API Key for AI services
- Telegram group chat IDs

### Local Installation
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

### Docker Installation
```bash
# Build and start containers
docker compose up -d

# View logs
docker compose logs -f
```

## Usage

1. **Receipt Processing**: Share receipt images in the configured Telegram group
2. **Data Analysis**: Send analysis prompts to the admin Telegram group
3. **Report Scheduling**: Configure `prompt.yaml` and send to the bot via personal chat

## CI/CD Pipeline

The project includes Jenkins pipeline configurations for:
- Continuous Integration (testing and image building)
- Continuous Deployment to test and production environments

## Project Structure

Key directories:
- `app/agents`: AI components for data processing
- `app/models`: Database models
- `app/controllers`: Business logic
- `app/routers`: API endpoints
- `app/commands`: Scheduled tasks
- `app/utils`: Utility functions
- `app/public`: Generated reports and uploads

## License

[Your License Information]
