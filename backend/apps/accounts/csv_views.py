"""
Views for CSV import functionality.

This module provides API endpoints for uploading, validating, previewing,
and importing employee roster data via CSV files.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .csv_import import EmployeeCSVImporter
from .csv_serializers import (
    CSVUploadSerializer, 
    CSVValidationResultSerializer,
    CSVImportConfirmSerializer
)


class CSVUploadValidateView(APIView):
    """
    Upload and validate CSV file.
    
    This endpoint accepts a CSV file upload, validates its format and content,
    and returns validation results with errors and warnings.
    
    Does not persist data - only validates.
    """
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """Upload and validate CSV file."""
        # Check if user is HR
        if not request.user.is_hr:
            return Response(
                {'detail': 'Only HR administrators can import employee data'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CSVUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = serializer.validated_data['file']
        
        # Parse and validate CSV
        importer = EmployeeCSVImporter()
        success, result = importer.parse_csv(csv_file)
        
        return Response(
            result,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Upload and Validate CSV",
        description="""
        Upload a CSV file containing employee roster data for validation.
        
        **Required CSV Columns:**
        - employee_id: Unique employee identifier
        - name: Full name (2-100 characters)
        - email: Valid email address (must be unique)
        - department: Department name
        - level: Employee level/grade
        
        **Optional CSV Columns:**
        - manager_id: Employee ID of the manager
        - start_date: Employment start date (YYYY-MM-DD)
        - region: Geographic region
        - job_title: Job title
        - phone: Contact phone number
        
        **Validation Checks:**
        - Email uniqueness (BR-008)
        - Manager references (BR-009)
        - Hierarchy depth and circular references (BR-010)
        - Data format and required fields
        
        **Response includes:**
        - Parsed data preview
        - Validation errors (blocking issues)
        - Validation warnings (non-blocking issues)
        - Summary with import eligibility
        """,
        request=CSVUploadSerializer,
        responses={
            200: CSVValidationResultSerializer,
            400: OpenApiResponse(description='Invalid file or validation errors'),
            403: OpenApiResponse(description='Permission denied - HR only')
        }
    )
    def post(self, request):
        return super().post(request)


class CSVImportConfirmView(APIView):
    """
    Confirm and execute CSV import.
    
    This endpoint receives validated employee data and imports it into
    the database. Import is atomic (BR-011) - either all records succeed
    or all fail.
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Execute CSV import with validated data."""
        # Check if user is HR
        if not request.user.is_hr:
            return Response(
                {'detail': 'Only HR administrators can import employee data'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CSVImportConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        parsed_data = serializer.validated_data['parsed_data']
        
        # Execute import
        importer = EmployeeCSVImporter()
        success, result = importer.import_employees(parsed_data)
        
        if success:
            return Response(
                result,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Confirm CSV Import",
        description="""
        Execute the import of validated employee data into the database.
        
        **Important:**
        - Data must be pre-validated using the upload/validate endpoint
        - Import is atomic (BR-011): all records succeed or all fail
        - Cannot import data with validation errors
        - Existing employees will be updated, new ones created
        - Manager relationships are established after user creation
        
        **Import Process:**
        1. Create/update departments
        2. Create/update employee records
        3. Establish manager relationships
        4. Assign default roles
        
        **Default Values:**
        - Password: ChangeMe123! (must be changed on first login)
        - Role: 'employee' (upgraded to 'manager' if they manage others)
        - Status: 'active'
        """,
        request=CSVImportConfirmSerializer,
        responses={
            201: OpenApiResponse(description='Import successful'),
            400: OpenApiResponse(description='Import failed or validation errors'),
            403: OpenApiResponse(description='Permission denied - HR only')
        }
    )
    def post(self, request):
        return super().post(request)


class CSVTemplateDownloadView(APIView):
    """
    Download CSV template for employee import.
    
    Provides a CSV template file with headers and example rows
    to help HR administrators format their employee data correctly.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Download CSV template."""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="employee_import_template.csv"'
        
        writer = csv.writer(response)
        
        # Write headers
        writer.writerow([
            'employee_id', 'name', 'email', 'department', 'level',
            'manager_id', 'start_date', 'region', 'job_title', 'phone'
        ])
        
        # Write example rows
        writer.writerow([
            'EMP001', 'John Doe', 'john.doe@company.com', 'Engineering', 
            'Senior', 'MGR001', '2023-01-15', 'US-West', 'Senior Engineer', '+12025551234'
        ])
        writer.writerow([
            'MGR001', 'Jane Smith', 'jane.smith@company.com', 'Engineering', 
            'Manager', '', '2020-03-01', 'US-West', 'Engineering Manager', '+12025555678'
        ])
        writer.writerow([
            'EMP002', 'Bob Johnson', 'bob.johnson@company.com', 'Sales', 
            'Mid', 'MGR002', '2022-06-01', 'US-East', 'Sales Associate', '+12025559012'
        ])
        
        return response
    
    @extend_schema(
        summary="Download CSV Template",
        description="""
        Download a CSV template file with the correct format for employee import.
        
        The template includes:
        - All required and optional column headers
        - Example rows showing proper data format
        - Comments explaining each field
        
        Use this template to ensure your CSV file is formatted correctly
        before uploading for validation and import.
        """,
        responses={
            200: OpenApiResponse(description='CSV template file')
        }
    )
    def get(self, request):
        return super().get(request)

