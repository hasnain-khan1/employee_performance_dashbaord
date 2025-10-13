"""
CSV Import functionality for employee roster.

This module handles CSV upload, validation, and import of employee data
with comprehensive error checking and hierarchy validation.

Implements Business Rules BR-008, BR-009, BR-010, BR-011.
"""

import csv
import io
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User
from apps.org.models import Department


class CSVValidationError:
    """Represents a validation error for a specific row."""
    
    def __init__(self, row_number: int, field: str, message: str, severity: str = 'error'):
        self.row_number = row_number
        self.field = field
        self.message = message
        self.severity = severity  # 'error' or 'warning'
    
    def to_dict(self):
        return {
            'row_number': self.row_number,
            'field': self.field,
            'message': self.message,
            'severity': self.severity
        }


class EmployeeCSVImporter:
    """
    Handles CSV import of employee roster data.
    
    Validates data quality, organizational hierarchy, and business rules
    before importing employees into the system.
    """
    
    REQUIRED_COLUMNS = ['employee_id', 'name', 'email', 'department', 'level']
    OPTIONAL_COLUMNS = ['manager_id', 'start_date', 'region', 'job_title', 'phone']
    ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
    
    MAX_HIERARCHY_DEPTH = 10  # BR-010
    
    def __init__(self):
        self.errors: List[CSVValidationError] = []
        self.warnings: List[CSVValidationError] = []
        self.parsed_data: List[Dict] = []
        self.employee_ids_in_csv = set()
        self.emails_in_csv = set()
    
    def parse_csv(self, csv_file) -> Tuple[bool, Dict]:
        """
        Parse and validate CSV file.
        
        Returns:
            Tuple of (success, result_dict)
            result_dict contains: parsed_data, errors, warnings, summary
        """
        self.errors = []
        self.warnings = []
        self.parsed_data = []
        self.employee_ids_in_csv = set()
        self.emails_in_csv = set()
        
        try:
            # Read CSV content
            content = csv_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            csv_file_io = io.StringIO(content)
            reader = csv.DictReader(csv_file_io)
            
            # Validate headers
            if not self._validate_headers(reader.fieldnames):
                return False, self._build_result()
            
            # Parse rows
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
                self._parse_row(row_num, row)
            
            # Perform cross-row validations
            if not self.errors:  # Only if no parsing errors
                self._validate_hierarchy()
                self._validate_manager_references()
                self._validate_uniqueness_with_db()
            
            success = len(self.errors) == 0
            return success, self._build_result()
            
        except Exception as e:
            self.errors.append(CSVValidationError(
                row_number=0,
                field='file',
                message=f'Error reading CSV file: {str(e)}'
            ))
            return False, self._build_result()
    
    def _validate_headers(self, headers: List[str]) -> bool:
        """Validate that all required columns are present."""
        if not headers:
            self.errors.append(CSVValidationError(
                row_number=0,
                field='headers',
                message='CSV file is empty or has no headers'
            ))
            return False
        
        # Normalize headers (strip whitespace, lowercase)
        normalized_headers = [h.strip().lower() for h in headers]
        
        missing_columns = []
        for required in self.REQUIRED_COLUMNS:
            if required.lower() not in normalized_headers:
                missing_columns.append(required)
        
        if missing_columns:
            self.errors.append(CSVValidationError(
                row_number=0,
                field='headers',
                message=f'Missing required columns: {", ".join(missing_columns)}'
            ))
            return False
        
        return True
    
    def _parse_row(self, row_num: int, row: Dict):
        """Parse and validate a single row."""
        # Normalize keys
        normalized_row = {k.strip().lower(): v.strip() if v else '' for k, v in row.items()}
        
        employee_data = {}
        row_has_errors = False
        
        # Validate employee_id (required)
        employee_id = normalized_row.get('employee_id', '').strip()
        if not employee_id:
            self.errors.append(CSVValidationError(
                row_num, 'employee_id', 'Employee ID is required'
            ))
            row_has_errors = True
        elif not re.match(r'^[A-Z0-9_-]+$', employee_id, re.IGNORECASE):
            self.errors.append(CSVValidationError(
                row_num, 'employee_id', 
                'Employee ID can only contain letters, numbers, hyphens, and underscores'
            ))
            row_has_errors = True
        elif employee_id in self.employee_ids_in_csv:
            self.errors.append(CSVValidationError(
                row_num, 'employee_id', 
                f'Duplicate employee ID: {employee_id}'
            ))
            row_has_errors = True
        else:
            self.employee_ids_in_csv.add(employee_id)
            employee_data['employee_id'] = employee_id
        
        # Validate name (required)
        name = normalized_row.get('name', '').strip()
        if not name:
            self.errors.append(CSVValidationError(
                row_num, 'name', 'Name is required'
            ))
            row_has_errors = True
        elif len(name) < 2 or len(name) > 100:
            self.errors.append(CSVValidationError(
                row_num, 'name', 'Name must be between 2 and 100 characters'
            ))
            row_has_errors = True
        else:
            # Split name into first and last
            name_parts = name.split(maxsplit=1)
            employee_data['first_name'] = name_parts[0]
            employee_data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
            employee_data['full_name'] = name
        
        # Validate email (required) - BR-008
        email = normalized_row.get('email', '').strip().lower()
        if not email:
            self.errors.append(CSVValidationError(
                row_num, 'email', 'Email is required'
            ))
            row_has_errors = True
        else:
            try:
                validate_email(email)
                if email in self.emails_in_csv:
                    self.errors.append(CSVValidationError(
                        row_num, 'email', 
                        f'Duplicate email address: {email} (BR-008: Email must be unique)'
                    ))
                    row_has_errors = True
                else:
                    self.emails_in_csv.add(email)
                    employee_data['email'] = email
            except ValidationError:
                self.errors.append(CSVValidationError(
                    row_num, 'email', 
                    f'Invalid email format: {email}'
                ))
                row_has_errors = True
        
        # Validate department (required)
        department = normalized_row.get('department', '').strip()
        if not department:
            self.errors.append(CSVValidationError(
                row_num, 'department', 'Department is required'
            ))
            row_has_errors = True
        else:
            employee_data['department'] = department
        
        # Validate level (required)
        level = normalized_row.get('level', '').strip()
        if not level:
            self.errors.append(CSVValidationError(
                row_num, 'level', 'Level is required'
            ))
            row_has_errors = True
        else:
            employee_data['level'] = level
        
        # Optional: manager_id - BR-009
        manager_id = normalized_row.get('manager_id', '').strip()
        if manager_id:
            employee_data['manager_id'] = manager_id
        
        # Optional: start_date
        start_date = normalized_row.get('start_date', '').strip()
        if start_date:
            parsed_date = self._parse_date(start_date)
            if parsed_date:
                employee_data['hire_date'] = parsed_date
            else:
                self.warnings.append(CSVValidationError(
                    row_num, 'start_date', 
                    f'Invalid date format: {start_date}. Expected YYYY-MM-DD',
                    severity='warning'
                ))
        
        # Optional: region
        region = normalized_row.get('region', '').strip()
        if region:
            employee_data['region'] = region
        
        # Optional: job_title
        job_title = normalized_row.get('job_title', '').strip()
        if job_title:
            employee_data['job_title'] = job_title
        elif level:
            # Use level as job_title if not provided
            employee_data['job_title'] = level
        
        # Optional: phone
        phone = normalized_row.get('phone', '').strip()
        if phone:
            employee_data['phone'] = phone
        
        # Store row data even if it has errors (for preview)
        employee_data['row_number'] = row_num
        employee_data['has_errors'] = row_has_errors
        self.parsed_data.append(employee_data)
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string in various formats."""
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return None
    
    def _validate_manager_references(self):
        """Validate that all manager_id references exist in the CSV. (BR-009)"""
        for employee in self.parsed_data:
            if employee.get('has_errors'):
                continue
            
            manager_id = employee.get('manager_id')
            if manager_id and manager_id not in self.employee_ids_in_csv:
                # Check if manager exists in database
                if not User.objects.filter(employee_id=manager_id).exists():
                    self.errors.append(CSVValidationError(
                        employee['row_number'], 'manager_id',
                        f'Manager ID {manager_id} not found in CSV or database (BR-009: Manager must exist)'
                    ))
    
    def _validate_hierarchy(self):
        """Validate organizational hierarchy for circular references and depth. (BR-010)"""
        # Build hierarchy map
        hierarchy = {}
        for employee in self.parsed_data:
            if employee.get('has_errors'):
                continue
            emp_id = employee.get('employee_id')
            manager_id = employee.get('manager_id')
            if emp_id:
                hierarchy[emp_id] = manager_id
        
        # Check for circular references
        for emp_id in hierarchy:
            if self._has_circular_reference(emp_id, hierarchy):
                # Find the row number
                row_num = next(
                    (e['row_number'] for e in self.parsed_data if e.get('employee_id') == emp_id),
                    0
                )
                self.errors.append(CSVValidationError(
                    row_num, 'manager_id',
                    f'Circular reporting relationship detected for employee {emp_id}'
                ))
        
        # Check hierarchy depth (BR-010)
        for emp_id in hierarchy:
            depth = self._get_hierarchy_depth(emp_id, hierarchy)
            if depth > self.MAX_HIERARCHY_DEPTH:
                row_num = next(
                    (e['row_number'] for e in self.parsed_data if e.get('employee_id') == emp_id),
                    0
                )
                self.errors.append(CSVValidationError(
                    row_num, 'manager_id',
                    f'Hierarchy depth exceeds maximum of {self.MAX_HIERARCHY_DEPTH} levels (BR-010)'
                ))
    
    def _has_circular_reference(self, emp_id: str, hierarchy: Dict, visited: set = None) -> bool:
        """Check if employee has circular reporting relationship."""
        if visited is None:
            visited = set()
        
        if emp_id in visited:
            return True
        
        visited.add(emp_id)
        manager_id = hierarchy.get(emp_id)
        
        if manager_id and manager_id in hierarchy:
            return self._has_circular_reference(manager_id, hierarchy, visited)
        
        return False
    
    def _get_hierarchy_depth(self, emp_id: str, hierarchy: Dict, depth: int = 0) -> int:
        """Calculate hierarchy depth for an employee."""
        if depth > self.MAX_HIERARCHY_DEPTH:
            return depth
        
        manager_id = hierarchy.get(emp_id)
        if not manager_id or manager_id not in hierarchy:
            return depth
        
        return self._get_hierarchy_depth(manager_id, hierarchy, depth + 1)
    
    def _validate_uniqueness_with_db(self):
        """Check for conflicts with existing database records. (BR-008)"""
        # Check employee IDs
        existing_employee_ids = set(
            User.objects.filter(
                employee_id__in=self.employee_ids_in_csv
            ).values_list('employee_id', flat=True)
        )
        
        for emp_id in existing_employee_ids:
            row_num = next(
                (e['row_number'] for e in self.parsed_data if e.get('employee_id') == emp_id),
                0
            )
            self.errors.append(CSVValidationError(
                row_num, 'employee_id',
                f'Employee ID {emp_id} already exists in the database'
            ))
        
        # Check emails (BR-008)
        existing_emails = set(
            User.objects.filter(
                email__in=self.emails_in_csv
            ).values_list('email', flat=True)
        )
        
        for email in existing_emails:
            row_num = next(
                (e['row_number'] for e in self.parsed_data if e.get('email') == email),
                0
            )
            self.errors.append(CSVValidationError(
                row_num, 'email',
                f'Email {email} already exists in the database (BR-008: Email must be unique)'
            ))
    
    def _build_result(self) -> Dict:
        """Build result dictionary with parsed data and validation results."""
        return {
            'parsed_data': self.parsed_data,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': [w.to_dict() for w in self.warnings],
            'summary': {
                'total_rows': len(self.parsed_data),
                'valid_rows': len([e for e in self.parsed_data if not e.get('has_errors')]),
                'error_count': len(self.errors),
                'warning_count': len(self.warnings),
                'can_import': len(self.errors) == 0
            }
        }
    
    @transaction.atomic  # BR-011: Atomic import
    def import_employees(self, validated_data: List[Dict]) -> Tuple[bool, Dict]:
        """
        Import validated employee data into the database.
        
        This is an atomic operation - either all records are imported
        or none are (BR-011).
        
        Args:
            validated_data: List of validated employee dictionaries
        
        Returns:
            Tuple of (success, result_dict)
        """
        if not validated_data:
            return False, {'message': 'No data to import'}
        
        try:
            created_employees = []
            created_count = 0
            updated_count = 0
            
            # First pass: Create/update departments
            departments = {}
            for emp_data in validated_data:
                if emp_data.get('has_errors'):
                    continue
                
                dept_name = emp_data.get('department')
                if dept_name and dept_name not in departments:
                    dept, created = Department.objects.get_or_create(
                        name=dept_name,
                        defaults={
                            'code': dept_name[:10].upper().replace(' ', '_'),
                            'description': f'Department: {dept_name}'
                        }
                    )
                    departments[dept_name] = dept
            
            # Second pass: Create users (without manager relationships)
            employee_mapping = {}
            for emp_data in validated_data:
                if emp_data.get('has_errors'):
                    continue
                
                employee_id = emp_data.get('employee_id')
                
                # Check if user already exists
                user, created = User.objects.get_or_create(
                    employee_id=employee_id,
                    defaults={
                        'username': employee_id.lower(),
                        'first_name': emp_data.get('first_name', ''),
                        'last_name': emp_data.get('last_name', ''),
                        'email': emp_data.get('email'),
                        'job_title': emp_data.get('job_title', emp_data.get('level', '')),
                        'hire_date': emp_data.get('hire_date'),
                        'phone': emp_data.get('phone', ''),
                        'department': departments.get(emp_data.get('department')),
                        'role': 'employee',  # Default role
                        'status': 'active'
                    }
                )
                
                if created:
                    # Set a default password (should be changed on first login)
                    user.set_password('ChangeMe123!')
                    user.save()
                    created_count += 1
                else:
                    # Update existing user
                    user.first_name = emp_data.get('first_name', user.first_name)
                    user.last_name = emp_data.get('last_name', user.last_name)
                    user.email = emp_data.get('email', user.email)
                    user.job_title = emp_data.get('job_title', emp_data.get('level', user.job_title))
                    user.department = departments.get(emp_data.get('department'), user.department)
                    if emp_data.get('hire_date'):
                        user.hire_date = emp_data.get('hire_date')
                    if emp_data.get('phone'):
                        user.phone = emp_data.get('phone')
                    user.save()
                    updated_count += 1
                
                employee_mapping[employee_id] = user
                created_employees.append(user)
            
            # Third pass: Set manager relationships
            for emp_data in validated_data:
                if emp_data.get('has_errors'):
                    continue
                
                employee_id = emp_data.get('employee_id')
                manager_id = emp_data.get('manager_id')
                
                if manager_id:
                    user = employee_mapping.get(employee_id)
                    manager = employee_mapping.get(manager_id)
                    
                    if not manager:
                        # Try to find manager in existing users
                        manager = User.objects.filter(employee_id=manager_id).first()
                    
                    if user and manager:
                        user.manager = manager
                        # Set manager role if they manage others
                        if manager.role == 'employee':
                            manager.role = 'manager'
                            manager.save()
                        user.save()
            
            return True, {
                'success': True,
                'message': f'Successfully imported {created_count} new employees and updated {updated_count} existing employees',
                'created_count': created_count,
                'updated_count': updated_count,
                'total_processed': len(created_employees)
            }
            
        except Exception as e:
            # Transaction will be rolled back automatically
            return False, {
                'success': False,
                'message': f'Import failed: {str(e)}',
                'detail': str(e)
            }

