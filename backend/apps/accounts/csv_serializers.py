"""
Serializers for CSV import functionality.
"""

from rest_framework import serializers


class CSVUploadSerializer(serializers.Serializer):
    """Serializer for CSV file upload."""
    
    file = serializers.FileField(
        help_text='CSV file containing employee roster data',
        required=True
    )
    
    def validate_file(self, value):
        """Validate the uploaded file."""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError(
                'File must be a CSV file with .csv extension'
            )
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f'File size cannot exceed 10MB. Current size: {value.size / 1024 / 1024:.2f}MB'
            )
        
        return value


class CSVValidationResultSerializer(serializers.Serializer):
    """Serializer for CSV validation results."""
    
    parsed_data = serializers.ListField(
        child=serializers.DictField(),
        help_text='Parsed employee data from CSV'
    )
    errors = serializers.ListField(
        child=serializers.DictField(),
        help_text='List of validation errors'
    )
    warnings = serializers.ListField(
        child=serializers.DictField(),
        help_text='List of validation warnings'
    )
    summary = serializers.DictField(
        help_text='Summary of validation results'
    )


class CSVImportConfirmSerializer(serializers.Serializer):
    """Serializer for confirming CSV import."""
    
    parsed_data = serializers.ListField(
        child=serializers.DictField(),
        help_text='Validated employee data to import',
        required=True
    )
    
    def validate_parsed_data(self, value):
        """Validate that data has no errors."""
        if not value:
            raise serializers.ValidationError('No data to import')
        
        # Check if any rows have errors
        error_rows = [row for row in value if row.get('has_errors')]
        if error_rows:
            raise serializers.ValidationError(
                f'Cannot import data with errors. {len(error_rows)} rows have validation errors.'
            )
        
        return value

