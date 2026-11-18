
import re
from urllib.parse import quote_plus

from agent.tool_executor import ToolExecutor
from mcp_integration.server_manager import mcp_server_manager
from llm_service import generate_response


class AgentEngine:

    def __init__(self):

        self.tool_executor = ToolExecutor(
            server_manager=mcp_server_manager
        )

    def understand_command(self, message):

        message = message.strip()
        lower_message = message.lower()

        # Open Chrome
        if lower_message in [
            "open chrome",
            "launch chrome",
            "start chrome"
        ]:
            return {
                "tool": "browser.open_chrome",
                "arguments": {}
            }

        # Close Chrome
        if lower_message in [
            "close chrome",
            "exit chrome",
            "stop chrome"
        ]:
            return {
                "tool": "browser.close_chrome",
                "arguments": {}
            }

        # Search request
        search_match = re.search(
            r"(?:search for|search|find)\s+(.+)",
            message,
            re.IGNORECASE
        )

        if search_match:

            query = search_match.group(1).strip()

            search_url = (
                "https://www.bing.com/search?q="
                + quote_plus(query)
            )

            return {
                "action": "browser_search",
                "query": query,
                "url": search_url
            }

        # Open URL
        url_match = re.search(
            r"https?://[^\s]+",
            message,
            re.IGNORECASE
        )

        if url_match:

            url = url_match.group(0).rstrip(".,!?")

            return {
                "tool": "browser.open_website",
                "arguments": {
                    "url": url
                }
            }

        # Open named website
        website_match = re.search(
            r"open\s+(?:the\s+)?(google|youtube|github|wikipedia)",
            lower_message
        )

        if website_match:

            websites = {
                "google": "https://www.google.com",
                "youtube": "https://www.youtube.com",
                "github": "https://github.com",
                "wikipedia": "https://www.wikipedia.org"
            }

            website = website_match.group(1)

            return {
                "tool": "browser.open_website",
                "arguments": {
                    "url": websites[website]
                }
            }

        return None

    async def run(self, message, conversation=None, model=None):

        command = self.understand_command(message)

        # Browser search through MCP
        if command and command.get("action") == "browser_search":

            try:

                server_name = "playwright"

                # Navigate to Google search
                navigation = await self.tool_executor.execute(
                    "mcp:playwright.browser_navigate",
                    {
                        "url": command["url"]
                    }
                )

                # Extract browser page content
                snapshot = await self.tool_executor.execute(
                    "mcp:playwright.browser_snapshot",
                    {}
                )

                browser_content = snapshot["result"]

                # Send extracted content to LLM
                result = generate_response(
                    user_message=(
                        "Summarize the following browser search results "
                        "for the user's request: "
                        + command["query"]
                        + "\n\nBrowser content:\n"
                        + str(browser_content)
                    ),
                    conversation=conversation,
                    model=model
                )

                return {
                    "success": result.get("success", True),
                    "type": "browser_search",
                    "query": command["query"],
                    "response": result.get("response", ""),
                    "browser_result": browser_content
                }

            except Exception as error:

                return {
                    "success": False,
                    "type": "browser_search",
                    "response": str(error)
                }

        # Execute normal recognized tools
        if command and command.get("tool"):

            try:

                result = await self.tool_executor.execute(
                    command["tool"],
                    command["arguments"]
                )

                return {
                    "success": True,
                    "type": "tool",
                    "response": result["result"],
                    "tool": result["tool"]
                }

            except Exception as error:

                return {
                    "success": False,
                    "type": "tool",
                    "response": str(error)
                }

        # List MCP tools
        if message.strip().lower() in [
            "list tools",
            "show available tools",
            "what tools are available"
        ]:

            tools = await mcp_server_manager.list_all_tools()

            return {
                "success": True,
                "type": "tools",
                "response": tools
            }

        # Normal chat fallback
        result = generate_response(
            user_message=message,
            conversation=conversation,
            model=model
        )

        return {
            "success": result.get("success", True),
            "type": "chat",
            "response": result.get("response", ""),
            "usage": result.get("usage")
        }


agent_engine = AgentEngine()
