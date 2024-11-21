This project is a **Human Resources Management System** built using FastAPI and SQLite, with Jinja2 templates for frontend rendering. The system provides functionalities to manage employee data, track attendance, calculate payroll, and generate summary reports on employee work hours and payroll expenses. Here's a breakdown of the features:

**Key Features:**

1. **Employee Management**:
   1. Add, edit, and delete employee details such as name, position, and hourly wage.
   1. View detailed employee profiles with attendance records.
1. **Attendance Tracking**:
   1. Record employee attendance with date and hours worked.
   1. View individual employee attendance records.
1. **Payroll Calculation**:
   1. Automatically calculate payroll based on hours worked and hourly wage.
   1. Display payroll details for all employees.
1. **Dashboard**:
   1. Visualize key metrics such as total employees, total hours worked, and total payroll.
1. **Database**:
- The system uses SQLite to store employee and attendance data.
- Ensures data integrity through foreign key relationships between employee and attendance records.

**Stack:**

- **Backend**: FastAPI for API handling and backend logic.
- **Database**: SQLite for persistent data storage.
- **Templates**: Jinja2 for dynamic HTML rendering.
- **Static Files**: CSS and JavaScript for frontend styling and interaction.

The application provides a streamlined HR management tool with a simple, user-friendly interface and comprehensive features for small to mid-sized businesses.
