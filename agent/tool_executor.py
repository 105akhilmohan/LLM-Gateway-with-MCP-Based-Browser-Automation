
class ToolExecutor:

    def __init__(self, server_manager=None):
        self.server_manager = server_manager

    async def execute(self, tool_name, arguments=None):

        if arguments is None:
            arguments = {}

        # Browser tools
        if tool_name == "browser.open_chrome":

            from browser.browser_service import open_chrome

            result = open_chrome(
                arguments.get("url")
            )

            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }

        if tool_name == "browser.open_website":

            from browser.browser_service import open_website

            result = open_website(
                arguments.get("url", "")
            )

            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }

        if tool_name == "browser.close_chrome":

            from browser.browser_service import close_chrome

            result = close_chrome()

            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }

        # MCP tools
        if tool_name.startswith("mcp:"):

            if not self.server_manager:
                raise RuntimeError("MCP server manager is not configured.")

            tool_path = tool_name.replace("mcp:", "", 1)

            if "." not in tool_path:
                raise ValueError(
                    "MCP tool must use the format mcp:server_name.tool_name"
                )

            server_name, mcp_tool_name = tool_path.split(".", 1)

            result = await self.server_manager.call_tool(
                server_name,
                mcp_tool_name,
                arguments
            )

            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }

        raise ValueError("Unknown tool: " + tool_name)
