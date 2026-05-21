from django.urls import path
from departments.views import DepartmentCreateAPIView, EmployeeCreateAPIView, DepartmentAPIView


urlpatterns = [
    path('departments/', DepartmentCreateAPIView.as_view(), name='department-create'),
    path('departments/<int:id>/employees/', EmployeeCreateAPIView.as_view(), name='employee-create'),
    path('departments/<int:id>/', DepartmentAPIView.as_view(), name='department-detail'),
]
