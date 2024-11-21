from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect('hr_management.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            hourly_rate REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            date TEXT,
            hours_worked REAL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Home Page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = sqlite3.connect('hr_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "employees": employees})

# Add Employee
@app.post("/add_employee", response_class=HTMLResponse)
async def add_employee(name: str = Form(...), position: str = Form(...), hourly_rate: float = Form(...)):
    conn = sqlite3.connect('hr_management.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, position, hourly_rate) VALUES (?, ?, ?)", (name, position, hourly_rate))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

# Record Attendance
@app.post("/add_attendance", response_class=HTMLResponse)
async def add_attendance(employee_id: int = Form(...), date: str = Form(...), hours_worked: float = Form(...)):
    conn = sqlite3.connect('hr_management.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (employee_id, date, hours_worked) VALUES (?, ?, ?)", (employee_id, date, hours_worked))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

# Payroll Calculation
@app.get("/payroll", response_class=HTMLResponse)
async def payroll(request: Request):
    conn = sqlite3.connect('hr_management.db')
    cursor = conn.cursor()
    
    # Modify the SQL query to use COALESCE to replace NULL with 0
    cursor.execute('''
        SELECT employees.name, employees.hourly_rate, COALESCE(SUM(attendance.hours_worked), 0) as total_hours
        FROM employees
        LEFT JOIN attendance ON employees.id = attendance.employee_id
        GROUP BY employees.id
    ''')
    payroll_data = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("payroll.html", {"request": request, "payroll_data": payroll_data})


# Employee Detail Page
@app.get("/employee/{employee_id}", response_class=HTMLResponse)
async def employee_detail(request: Request, employee_id: int):
    conn = sqlite3.connect('hr_management.db')
    cursor = conn.cursor()

    # Fetch employee details
    cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
    employee = cursor.fetchone()

    # Fetch attendance records for the employee
    cursor.execute("SELECT * FROM attendance WHERE employee_id = ?", (employee_id,))
    attendance_records = cursor.fetchall()
    
    conn.close()
    return templates.TemplateResponse("employee_detail.html", {"request": request, "employee": employee, "attendance_records": attendance_records})

# Edit Employee Information
@app.post("/edit_employee/{employee_id}", response_class=HTMLResponse)
async def edit_employee(employee_id: int, name: str = Form(...), position: str = Form(...), hourly_rate: float = Form(...)):
    conn = sqlite3.connect('hr_management.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE employees SET name = ?, position = ?, hourly_rate = ? WHERE id = ?", (name, position, hourly_rate, employee_id))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/employee/{employee_id}", status_code=303)

# Delete Employee
@app.post("/delete_employee/{employee_id}", response_class=HTMLResponse)
async def delete_employee(employee_id: int):
    conn = sqlite3.connect('hr_management.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    cursor.execute("DELETE FROM attendance WHERE employee_id = ?", (employee_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    conn = sqlite3.connect('hr_management.db')
    cursor = conn.cursor()

    # Total number of employees
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    # Total hours worked
    cursor.execute("SELECT SUM(hours_worked) FROM attendance")
    total_hours = cursor.fetchone()[0] or 0

    # Total payroll
    cursor.execute('''
        SELECT SUM(attendance.hours_worked * employees.hourly_rate)
        FROM attendance
        JOIN employees ON employees.id = attendance.employee_id
    ''')
    total_payroll = cursor.fetchone()[0] or 0

    conn.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "total_employees": total_employees, "total_hours": total_hours, "total_payroll": total_payroll})
