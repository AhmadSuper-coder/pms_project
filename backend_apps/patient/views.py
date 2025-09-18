from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Patient
from .serializers import PatientSerializer


class PatientCRUDView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id=None):
        if patient_id is None:
            patients = Patient.objects.filter(doctor=request.user).order_by('full_name')
            data = PatientSerializer(patients, many=True).data
            return Response({"results": data})
        try:
            patient = Patient.objects.get(id=patient_id, doctor=request.user)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PatientSerializer(patient).data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        patient = serializer.save(doctor=request.user)
        return Response(PatientSerializer(patient).data, status=status.HTTP_201_CREATED)

    def patch(self, request, patient_id=None):
        if patient_id is None:
            return Response({"detail": "patient_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            patient = Patient.objects.get(id=patient_id, doctor=request.user)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, patient_id=None):
        if patient_id is None:
            return Response({"detail": "patient_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            patient = Patient.objects.get(id=patient_id, doctor=request.user)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
