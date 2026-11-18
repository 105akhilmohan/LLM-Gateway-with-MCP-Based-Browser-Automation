
from mcp_integration.mcp_client import MCPClient


class MCPServerManager:

    def __init__(self):

        self.client = MCPClient()
        self.server_configs = {}

    def add_server(self, name, command, args=None, env=None):

        self.server_configs[name] = {
            "command": command,
            "args": args or [],
            "env": env
        }

    async def start_server(self, name):

        if name not in self.server_configs:
            raise ValueError("MCP server configuration not found: " + name)

        config = self.server_configs[name]

        return await self.client.connect(
            server_name=name,
            command=config["command"],
            args=config["args"],
            env=config["env"]
        )

    async def start_all(self):

        results = {}

        for name in self.server_configs:

            try:
                results[name] = await self.start_server(name)

            except Exception as error:
                results[name] = "Connection failed: " + str(error)

        return results

    async def list_servers(self):

        connected = []

        for name in self.client.sessions:

            connected.append({
                "name": name,
                "connected": True
            })

        return connected

    async def list_tools(self, server_name):

        return await self.client.list_tools(server_name)

    async def list_all_tools(self):

        all_tools = {}

        for server_name in self.client.sessions:

            all_tools[server_name] = await self.list_tools(
                server_name
            )

        return all_tools

    async def call_tool(self, server_name, tool_name, arguments=None):

        return await self.client.call_tool(
            server_name,
            tool_name,
            arguments
        )

    async def stop_server(self, name):

        return await self.client.disconnect(name)

    async def stop_all(self):

        await self.client.disconnect_all()


mcp_server_manager = MCPServerManager()

mcp_server_manager.add_server(
    name="playwright",
    command="cmd",
    args=[
        "/c",
        "npx",
        "-y",
        "@playwright/mcp@latest"
    ]
)