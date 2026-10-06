from fastmcp import FastMCP


mcp = FastMCP("Employee HR Server")


employees = {
    "EMP001": {
        "employee_name": "Jacky",
        "casual_leave": 5,
        "sick_leave": 3,
        "earned_leave": 10
    },
    "EMP002": {
        "employee_name": "Rahul",
        "casual_leave": 8,
        "sick_leave": 4,
        "earned_leave": 12
    }
}


@mcp.tool
def get_leave_balance(employee_id: str) -> dict:
    """Get the current leave balance of an employee."""

    employee = employees.get(employee_id)

    if employee is None:
        return {
            "success": False,
            "message": "Employee not found"
        }

    return {
        "success": True,
        "employee_id": employee_id,
        "employee_name": employee["employee_name"],
        "casual_leave": employee["casual_leave"],
        "sick_leave": employee["sick_leave"],
        "earned_leave": employee["earned_leave"]
    }


if __name__ == "__main__":

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000
    )