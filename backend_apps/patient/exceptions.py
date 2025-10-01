from non_django.error_handling.exceptions import GlobalException  # type: ignore


class PatientException(GlobalException):
    USER_ALREADY_EXIST = {0: "Patient has already been registered with this phone number."}


patient_exception = PatientException()