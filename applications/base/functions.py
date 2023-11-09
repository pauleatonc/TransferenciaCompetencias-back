from django.core.exceptions import ValidationError

# límite de tamaño para los archivos
FIVE_SIZE_LIMIT = 5 * 1024 * 1024  # 5 MB
TWENTY_SIZE_LIMIT = 20 * 1024 * 1024  # 20 MB


def validate_file_size_five(value):
    filesize = value.size

    if filesize > FIVE_SIZE_LIMIT:
        raise ValidationError("El archivo PDF no debe exceder los 5MB")
    else:
        return value


def validate_file_size_twenty(value):
    filesize = value.size

    if filesize > TWENTY_SIZE_LIMIT:
        raise ValidationError("El archivo PDF no debe exceder los 20MB")
    else:
        return value

