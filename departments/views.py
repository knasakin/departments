import logging

from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from departments.models import Department, Employee
from departments.serializers import DepartmentSerializer, EmployeeSerializer, DepartmentTreeSerializer


logger = logging.getLogger(__name__)


# POST api/departments/
class DepartmentCreateAPIView(CreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def perform_create(self, serializer):
        department = serializer.save()

        logger.info(
            'Department created. department_id=%s name=%s',
            department.id,
            department.name,
        )


# POST api/departments/{id}/employees/
class EmployeeCreateAPIView(CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def perform_create(self, serializer):
        department = get_object_or_404(Department, id=self.kwargs['id'])
        serializer.save(department=department)


# GET + PATCH + DELETE /departments/{id}
class DepartmentAPIView(APIView):
    def get(self, request, id):
        department = get_object_or_404(
            Department.objects.prefetch_related(
                'employees',
                'children',
            ),
            id=id,
        )

        try:
            depth = int(request.query_params.get('depth', 1))
        except (TypeError, ValueError):
            depth = 1

        depth = max(0, min(depth, 5))

        include_employees = (request.query_params.get('include_employees', 'true').lower() == 'true')

        serializer = DepartmentTreeSerializer(
            department,
            context={
                'depth': depth,
                'include_employees': include_employees
            }
        )

        return Response(serializer.data)

    def patch(self, request, id):
        department = get_object_or_404(Department, id=id)

        serializer = DepartmentSerializer(
            department,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, id):
        department = get_object_or_404(Department, id=id)

        mode = request.query_params.get('mode')
        if mode not in ('cascade', 'reassign'):
            return Response(
                data={'detail': 'Некорректный режим удаления'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if mode == 'cascade':
            department.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        reassign_to_department_id = request.query_params.get('reassign_to_department_id')
        if reassign_to_department_id is None:
            return Response(
                data={'detail': 'Параметр reassign_to_department_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reassign_department = get_object_or_404(Department, id=reassign_to_department_id)
        if department.id == reassign_department.id:
            return Response(
                data={'detail': 'Нельзя переназначить сотрудников в то же подразделение'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        department.employees.update(department=reassign_department)
        department.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

