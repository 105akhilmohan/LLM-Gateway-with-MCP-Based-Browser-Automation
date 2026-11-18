
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:

    def __init__(self):

        self.sessions = {}
        self.exit_stacks = {}

    async def connect(self, server_name, command, args=None, env=None):

        if server_name in self.sessions:
            return "MCP server is already connected."

        if args is None:
            args = []

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

        stack = AsyncExitStack()

        try:

            read_stream, write_stream = await stack.enter_async_context(
                stdio_client(server_params)
            )

            session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            await session.initialize()

            self.sessions[server_name] = session
            self.exit_stacks[server_name] = stack

            return "Connected to MCP server: " + server_name

        except Exception:

            await stack.aclose()
            raise

    async def list_tools(self, server_name):

        if server_name not in self.sessions:
            raise RuntimeError("MCP server is not connected.")

        session = self.sessions[server_name]

        result = await session.list_tools()

        tools = []

        for tool in result.tools:

            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            })

        return tools

    async def call_tool(self, server_name, tool_name, arguments=None):

        if server_name not in self.sessions:
            raise RuntimeError(
                f"MCP server '{server_name}' is not connected."
            )

        if arguments is None:
            arguments = {}

        session = self.sessions[server_name]

        result = await session.call_tool(
            tool_name,
            arguments=arguments
        )

        content = []

        for item in result.content:
            if hasattr(item, "text"):
                content.append(item.text)
            else:
                content.append(str(item))

        is_error = getattr(
            result,
            "isError",
            getattr(result, "is_error", False)
        )

        return {
            "is_error": is_error,
            "content": content
        }

    async def disconnect(self, server_name):

        if server_name not in self.exit_stacks:
            return "MCP server is not connected."

        stack = self.exit_stacks.pop(server_name)

        await stack.aclose()

        self.sessions.pop(server_name, None)

        return "Disconnected MCP server: " + server_name

    async def disconnect_all(self):

        for server_name in list(self.sessions.keys()):
            await self.disconnect(server_name)
