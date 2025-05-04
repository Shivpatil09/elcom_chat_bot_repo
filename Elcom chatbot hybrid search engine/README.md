# Elcom Chatbot Hybrid Search Engine

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

## Setup

### Backend (Rasa)

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install rasa
pip install -r requirements.txt
```

3. Train the Rasa model:
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