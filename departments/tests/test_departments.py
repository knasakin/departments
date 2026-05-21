from rest_framework import status
from rest_framework.test import APITestCase

from departments.models import Department


class DepartmentAPITestCase(APITestCase):
    def test_create_department(self):
        payload = {'name': 'Backend'}

        response = self.client.post(
            '/api/departments/',
            data=payload,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Department.objects.count(),
            1,
        )

        self.assertEqual(
            Department.objects.first().name,
            'Backend',
        )

    def test_department_cycle_validation(self):
        parent = Department.objects.create(
            name='Parent',
        )

        child = Department.objects.create(
            name='Child',
            parent=parent,
        )

        response = self.client.patch(
            f'/api/departments/{parent.id}/',
            data={'parent_id': child.id},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_delete_department_reassign_mode(self):
        old_department = Department.objects.create(
            name='Old Department',
        )

        new_department = Department.objects.create(
            name='New Department',
        )

        response = self.client.delete(
            f'/api/departments/{old_department.id}/?mode=reassign&reassign_to_department_id={new_department.id}',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Department.objects.filter(
                id=old_department.id,
            ).exists()
        )
