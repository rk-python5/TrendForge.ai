# LinkedIn AI Agent 🤖

An AI-powered agent that generates LinkedIn posts, manages approvals, and helps you maintain a consistent content presence.

## 🎯 Features

- **AI Content Generation**: Create engaging LinkedIn posts using local LLMs
- **Human-in-the-Loop**: Review and approve posts before publishing
- **Content Calendar**: Schedule and manage your content pipeline
- **Post Analytics**: Track performance and learn what works
- **100% Free**: Runs entirely on your machine using Ollama

## 🛠 Tech Stack

- **Python 3.10+**
- **Ollama** (Llama 3.2) - Local LLM
- **LangGraph** - Agent orchestration
- **SQLite** - Data storage
- **Rich** - Beautiful terminal UI

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Ollama installed
- VS Code (recommended)

### 2. Installation

```bash
# Clone/navigate to project
cd "social media ai agent"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your preferences

# Pull Ollama model
ollama pull llama3.2:3b
```

### 3. Run the Agent

```bash
python main.py
```

## 📁 Project Structure

```
social media ai agent/
├── agents/           # Agent implementations
├── graph/            # LangGraph workflow
├── tools/            # LLM and utility tools
├── storage/          # Database models
├── ui/               # User interfaces
├── config/           # Configuration
├── data/             # SQLite database
└── main.py           # Entry point
```

## 🎓 Learning Path

This project teaches:
- Agentic AI patterns
- LangGraph state management
- Human-in-the-loop workflows
- Prompt engineering
- Database design for agents

## 📝 Usage

1. **Generate Post**: Agent creates draft based on your topic
2. **Review**: Approve, reject, or request edits
3. **Save**: Approved posts saved to database
4. **Export**: Export to markdown for posting

## 🔜 Roadmap

- [x] Phase 1: Basic generation and approval
- [ ] Phase 2: Web UI and scheduling
- [ ] Phase 3: Automated posting
- [ ] Phase 4: Multi-platform (Instagram)

## 📄 License

MIT

## 🤝 Contributing

This is a learning project! Feel free to fork and experiment.
