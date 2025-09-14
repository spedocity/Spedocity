from .models import Employee

def employee_info(request):
    """Context processor to add employee information to the template context."""
    employee_info = {}

    # Check if the employee_id exists in the session
    employee_id = request.session.get('employee_id')

    if employee_id:
        try:
            # Retrieve the employee instance from the database
            employee = Employee.objects.get(id=employee_id)

            # Add employee details to the context
            employee_info = {
                'employee_id': employee.employee_id,
                'employee_name': f'{employee.first_name} {employee.last_name}',
                'employee_email': employee.email,
                'employee_phone': employee.phone_number,
            }

        except Employee.DoesNotExist:
            pass  # No employee found, keep employee_info empty

    return {'employee_info': employee_info}