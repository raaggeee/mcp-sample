import os
import random
import tempfile

import aiosqlite
from fastmcp import FastMCP

mcp = FastMCP(name="Demo Server")

TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")
CATEGORY_TYPE = os.path.join(os.path.dirname(__file__), "categories.json")


def init_db():
    import sqlite3

    try:
        with sqlite3.connect(DB_PATH) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses(
                exp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exp_name TEXT NOT NULL,
                exp_type TEXT NOT NULL,
                exp_amt INTEGER NOT NULL,
                exp_note TEXT NOT NULL
                )
                """
            )
        print("Database Initializaiton Successful!")
    except Exception as e:
        print("Database Initializaiton Failed!")
        print("Error:", e)


init_db()


@mcp.tool()
async def add_expense(name, type, amt, note):
    """Tool to add expenses.
    Args:
        name: Name of the expense
        type: Type of expense.
        amt: Expense amount
        note: Additional Note
    """
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                """
                INSERT INTO expenses (exp_name, exp_type, exp_amt, exp_note) VALUES (?, ?, ?, ?)
                """,
                (name, type, amt, note),
            )
            expense_id = cur.lastrowid
            await c.commit()
            return {
                "status": "ok",
                "id": expense_id,
                "message": "Added Expense Successfully!",
            }

    except Exception as e:
        return {"status": "error", "message": f"Database error: {e}"}


@mcp.tool()
async def list_expense(exp_type=None):
    """
    List of Expenses
    Args:
        exp_type: None or Type of expense.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            params_type = []
            query = """
            SELECT exp_id, exp_name, exp_type, exp_amt, exp_note FROM expenses
            """
            if exp_type:
                query += "WHERE exp_type = ?"
                params_type.append(exp_type)

            cur = await c.execute(query, params_type)

            cols = [d[0] for d in cur.description]

            return [dict(zip(cols, r)) for r in await cur.fetchall()]

    except Exception as e:
        return {"status": "error", "message": f"Database error: {e}"}


@mcp.tool()
async def list_category():
    "List of all expense categories"
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute("""
                    SELECT DISTINCT exp_type
                    FROM expenses
                """)

            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in await cur.fetchall()]

    except Exception as e:
        return {"status": "error", "message": f"Database error: {e}"}


@mcp.tool()
async def summarize_expense(exp_type=None):
    "Used for summarizing the expenses"
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            params = []
            query = """
                SELECT exp_type, SUM(exp_amt) AS amt
                FROM expenses
            """

            if exp_type:
                query += "WHERE exp_type = ?"
                params.append(exp_type)

            cur = await c.execute(query, params)

            col = [d[0] for d in cur.description]
            return [dict(zip(col, r)) for r in await cur.fetchall()]

    except Exception as e:
        return {"status": "error", "message": f"Database error: {e}"}


@mcp.tool()
def roll_dice(n_dice: int = 1):
    "Randomly roll n dices and return a list of values of dice"
    return [random.randint(1, 6) for _ in range(n_dice)]


@mcp.tool()
def add_numbers(a: int, b: int):
    "Function to add two numbers"
    return a + b


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open(CATEGORY_TYPE, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
