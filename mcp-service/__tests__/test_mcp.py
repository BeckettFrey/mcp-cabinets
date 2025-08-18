# File: mcp-service/__tests__/test_mcp.py
import pytest
from fastmcp import FastMCP, Client

# Mark all tests as async
pytestmark = pytest.mark.asyncio

@pytest.fixture
def simple_server():
    """Create a simple MCP server for testing"""
    mcp = FastMCP(name="TestServer")
    
    @mcp.tool()
    def add(a: int, b: int) -> int:
        """Add two integers together"""
        return a + b
    
    @mcp.tool()
    def divide(a: int, b: int) -> float:
        """Divide two numbers"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    @mcp.tool()
    def get_status() -> str:
        """Get server status"""
        return "OK"
    
    return mcp

async def test_server_ping(simple_server):
    """Test server connectivity"""
    async with Client(simple_server) as client:
        is_alive = await client.ping()
        assert is_alive

async def test_list_tools(simple_server):
    """Test that tools are properly listed"""
    async with Client(simple_server) as client:
        tools = await client.list_tools()
        # tools is now a list, not an object with .tools attribute
        tool_names = [tool.name for tool in tools]
        assert "add" in tool_names
        assert "divide" in tool_names
        assert "get_status" in tool_names
        assert len(tools) == 3

async def test_call_tool_add(simple_server):
    """Test calling the add tool"""
    async with Client(simple_server) as client:
        result = await client.call_tool("add", {"a": 5, "b": 3})
        # Result is now a CallToolResult object, not subscriptable
        # Access the content directly
        assert str(result.content[0].text) == "8"

async def test_call_tool_divide(simple_server):
    """Test calling the divide tool"""
    async with Client(simple_server) as client:
        result = await client.call_tool("divide", {"a": 10, "b": 2})
        assert str(result.content[0].text) == "5.0"

async def test_call_tool_status(simple_server):
    """Test calling the status tool"""
    async with Client(simple_server) as client:
        result = await client.call_tool("get_status", {})
        assert str(result.content[0].text) == "OK"

async def test_error_handling_divide_by_zero(simple_server):
    """Test error handling for divide by zero"""
    async with Client(simple_server) as client:
        # This should raise an exception or return an error result
        try:
            result = await client.call_tool("divide", {"a": 10, "b": 0})
            # If no exception is raised, check if error is in result
            assert result.isError or "error" in str(result.content[0].text).lower()
        except Exception as e:
            # Exception was raised as expected
            assert "divide by zero" in str(e).lower() or "cannot divide by zero" in str(e).lower()

async def test_invalid_tool_name(simple_server):
    """Test calling a non-existent tool"""
    async with Client(simple_server) as client:
        try:
            result = await client.call_tool("nonexistent_tool", {})
            # If no exception, check for error in result
            assert result.isError
        except Exception:
            # Exception was raised as expected
            pass

async def test_invalid_tool_parameters(simple_server):
    """Test calling a tool with invalid parameters"""
    async with Client(simple_server) as client:
        try:
            # Missing required parameter
            result = await client.call_tool("add", {"a": 5})  # missing 'b'
            # If no exception, check for error in result
            assert result.isError
        except Exception:
            # Exception was raised as expected
            pass

# More comprehensive server for advanced testing
@pytest.fixture  
def advanced_server():
    """Create a more complex server for advanced testing"""
    mcp = FastMCP(name="AdvancedTestServer")
    
    @mcp.tool()
    def calculate(operation: str, a: float, b: float) -> float:
        """Perform basic calculations"""
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    @mcp.tool()
    def echo(message: str) -> str:
        """Echo back the message"""
        return f"Echo: {message}"
    
    return mcp

async def test_advanced_calculator(advanced_server):
    """Test the advanced calculator tool"""
    async with Client(advanced_server) as client:
        # Test addition
        result = await client.call_tool("calculate", {
            "operation": "add", 
            "a": 10.5, 
            "b": 5.3
        })
        assert float(result.content[0].text) == 15.8
        
        # Test multiplication
        result = await client.call_tool("calculate", {
            "operation": "multiply", 
            "a": 4, 
            "b": 3
        })
        assert float(result.content[0].text) == 12.0

async def test_echo_tool(advanced_server):
    """Test the echo tool"""
    async with Client(advanced_server) as client:
        test_message = "Hello, World!"
        result = await client.call_tool("echo", {"message": test_message})
        assert str(result.content[0].text) == f"Echo: {test_message}"

async def test_multiple_clients_same_server(simple_server):
    """Test that multiple clients can connect to the same server"""
    async with Client(simple_server) as client1:
        async with Client(simple_server) as client2:
            # Both clients should be able to ping
            assert await client1.ping()
            assert await client2.ping()
            
            # Both should be able to call tools
            result1 = await client1.call_tool("add", {"a": 1, "b": 2})
            result2 = await client2.call_tool("add", {"a": 3, "b": 4})
            
            assert str(result1.content[0].text) == "3"
            assert str(result2.content[0].text) == "7"

# Performance test
async def test_rapid_tool_calls(simple_server):
    """Test making many rapid tool calls"""
    async with Client(simple_server) as client:
        results = []
        for i in range(10):
            result = await client.call_tool("add", {"a": i, "b": 1})
            results.append(int(result.content[0].text))
        
        # Verify all results are correct
        for i, result in enumerate(results):
            assert result == i + 1