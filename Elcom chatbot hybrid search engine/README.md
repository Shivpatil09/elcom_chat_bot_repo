# Elcom Chatbot Hybrid Search Engine

⚠️ **IMPORTANT: This project requires Python version between 3.7 and 3.9 ONLY. Python 3.10 or higher will NOT work.**

A hybrid search-based chatbot system for Elcom's product catalog, built with Rasa and React.

## Features

- Natural language product search
- Hybrid search algorithm combining semantic and keyword-based matching
- Real-time product information retrieval
- Modern React-based chat interface
- Full-screen and resizable chat window
- Markdown support for formatted responses

## Project Structure

- `frontend/` - React-based chat interface
- `actions/` - Custom Rasa actions for product search
- `data/` - Rasa training data (NLU, stories, rules)
- `tests/` - Test files for Rasa and product queries

## Python Version Requirement

⚠️ **CRITICAL: Python Version Compatibility**
- **Required**: Python 3.7.x to 3.9.x ONLY
- **Will NOT work with**: Python 3.10 or higher
- **Best Performance**: Python 3.9.x
- **Tested versions**:
  - Python 3.7.0 to 3.7.16
  - Python 3.8.0 to 3.8.16
  - Python 3.9.0 to 3.9.16

If you have multiple Python versions installed, make sure you're using a compatible version:
```bash
# Check Python version
python --version  # Should show 3.7.x, 3.8.x, or 3.9.x

# If needed, you can specifically use python3.9 or python3.8
# Example: python3.9 -m venv venv
```

## Other Requirements
- Node.js 14+ (for frontend)

## Setup

### Backend (Rasa)

1. Create a Python virtual environment:
```bash
# IMPORTANT: Verify you have the correct Python version installed
python --version  # MUST show version between 3.7.0 and 3.9.16
# If incorrect version, stop and install correct Python version first

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
# On Windows:
python -m pip install --upgrade pip
pip install -r requirements.txt

# On Linux/Mac:
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

# If you encounter any issues with dependencies, try:
pip install -r requirements.txt --no-cache-dir
```

3. Verify installation:
```bash
rasa --version
python -c "import rasa"  # Should not show any errors
```

4. Train the Rasa model:
```bash
rasa train
```

4. Start Rasa services:
```bash
# Start Rasa server
rasa run --enable-api --cors "*"

# In a new terminal, start actions server
rasa run actions
```

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

## Configuration

- `config.yml` - Rasa pipeline configuration
- `domain.yml` - Chatbot domain configuration
- `endpoints.yml` - Service endpoint configuration
- `credentials.yml` - Authentication credentials

## API Documentation

The chatbot exposes a REST API endpoint for communication:

- `POST /webhooks/rest/webhook` - Send messages to the chatbot
- Request format: `{ "message": "your message here" }`
- Response format: Array of `{ "text": "bot response" }`

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

Proprietary - Elcom internal use only