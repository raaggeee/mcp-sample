import random

from fastmcp import FastMCP

mcp = FastMCP(name="Demo Server")


@mcp.tool()
def roll_dice(n_dice: int = 1):
    "Randomly roll n dices and return a list of values of dice"
    return [random.randint(1, 6) for _ in range(n_dice)]


@mcp.tool()
def add_numbers(a: int, b: int):
    "Function to add two numbers"
    return a + b


if __name__ == "__main__":
    mcp.run()
