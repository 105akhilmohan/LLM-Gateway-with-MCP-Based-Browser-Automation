# LLM Gateway with AI Agent and MCP-Based Browser Automation

## Project Description

LLM Gateway is an AI-powered application that provides a centralized interface for interacting with multiple Large Language Models (LLMs). It integrates the OpenRouter API to access different LLM models through a unified gateway.

The application uses an AI Agent to understand natural-language instructions, identify the required actions, and execute tasks using available tools.

It also integrates the Model Context Protocol (MCP) with Playwright to enable browser automation. Users can provide commands such as searching for Python developer jobs, opening websites, and navigating web pages. The AI Agent processes these instructions and uses browser automation tools to perform the requested actions.

The project combines LLM integration, AI agent execution, MCP tool integration, and browser automation in a single application.

## Key Features

- **Centralized LLM Access:** Connects to multiple LLM models using OpenRouter.
- **AI Agent:** Understands user instructions and determines the appropriate actions.
- **MCP Integration:** Connects external tools through the Model Context Protocol.
- **Browser Automation:** Uses Playwright MCP to automate browser navigation.
- **Natural Language Interaction:** Allows users to execute tasks using simple text commands.
- **Tool Execution:** Selects and executes tools based on user requests.
- **Interactive Chat Interface:** Provides a web-based interface for interacting with the AI system.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | Backend API framework |
| OpenRouter API | Access to multiple LLM models |
| Model Context Protocol (MCP) | External tool integration |
| Playwright | Browser automation |
| Node.js and npm | MCP server execution |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | Frontend interaction |

## System Architecture

The application follows this workflow:

1. The user enters a natural-language command through the web interface.
2. FastAPI receives the user's request.
3. The AI Agent analyzes the instruction.
4. The agent determines whether an external tool is required.
5. The MCP client communicates with the Playwright MCP server.
6. Playwright performs browser actions such as opening websites and searching for information.
7. The result is returned to the agent.
8. The application displays the response to the user.

*Note: Adjust the structure above to match your actual project files.*

## Installation and Setup

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory.

Add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

Replace the placeholder with your actual API key.

### 5. Install Node.js

Install Node.js and npm if they are not already installed. The Playwright MCP server is launched using `npx`.

### 6. Run the Application

```bash
uvicorn app:app --reload --port 8002
```

Open the application in your browser:

```text
http://127.0.0.1:8002/
```

## Example Commands

Users can interact with the AI Agent using commands such as:

- Open Chrome.
- Open YouTube.
- Open GitHub.
- Search for Python developer jobs.
- Search for machine learning engineer jobs.
- Open a website.

## Future Enhancements

- Support additional MCP servers and external tools.
- Improve browser-based information extraction.
- Add support for more complex multi-step agent tasks.
- Introduce conversation history and session management.
- Improve error handling and agent execution monitoring.
- Support additional LLM providers.

## License

This project is intended for educational and development purposes.
