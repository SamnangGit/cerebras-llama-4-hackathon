# Installation Guide

## Project Setup

### Environment Configuration (.env)
```dotenv
# Application
APP_ENV=
TELEGRAM_BOT_TOKEN=

# Database
DB_CONNECTION=postgresql+psycopg2
DB_HOST=db
DB_PORT=5432
DB_DATABASE=FuelTransactionDB
DB_USERNAME=postgres
DB_PASSWORD=

# External Services
GOOGLE_API_KEY=

# Telegram
CAR_GROUP_CHAT_ID=
ADMIN_GROUP_CHAT_ID=
PERSONAL_CHAT_ID=
```

> Note: Configure with your environment variables
> <br>
> <b>CAR_GROUP_CHAT_ID:</b> For Data Extraction
> <br>
> <b>ADMIN_GROUP_CHAT_ID:</b> For Data Analysis
> <br>
> <b>PERSONAL_CHAT_ID:</b> For Scheduler Configuration
> <br>

## Local Installation
1. **Navigate to the Root Directory**  
   ```bash
   cd /path/to/your/project
   ```

2. **Create and Activate Python Virtual Environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env File and Put in Your API Key**  
   ```bash
   cp .envexample .env
   ```
   Edit the `.env` file to include your telegram bot token and other variable.

5. **Navigate to the App Directory**  
   ```bash
   cd path/to/your/project/app
   ```

6. **Serve the Application**  
   ```bash
   uvicorn main:app --reload
   ```

## Docker Installation
1. **Ensure Docker and Compose are Installed**  
   Install Docker on your system if not already installed.

2. **Navigate to the Root Directory**  
   ```bash
   cd /path/to/your/project
   ```

3. **Build and Run the Application with Docker Compose**:
   ```bash
   docker compose up -d
   ```

4. **View Logs** (optional):
   ```bash
   docker compose logs -f
   ```

5. **Stop and Remove Containers**:
   ```bash
   docker compose down
   ```
