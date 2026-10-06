from fastmcp import FastMCP

mcp = FastMCP("Employee HR Server")


@mcp.tool
def get_leave_balance(employee_id: str) -> dict:
    """
    Get the current leave balance for an employee.
    """

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

    employee = employees.get(employee_id)

    if employee is None:
        return {
            "error": "Employee not found"
        }

    return employee


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000
    )