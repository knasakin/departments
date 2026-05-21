from django.db import models


class DepartmentQuerySet(models.QuerySet):
    pass


class EmployeeQuerySet(models.QuerySet):
    pass


class Department(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )

    objects = DepartmentQuerySet.as_manager()

    class Meta:
        ordering = ('id',)
        verbose_name = 'Департамент'
        verbose_name_plural = 'Департаменты'
        constraints = [
            models.UniqueConstraint(
                fields=('parent', 'name'),
                name='unique_department_name_per_parent',
            ),
        ]

    def __str__(self):
        return self.name


class Employee(models.Model):
    full_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)

    hired_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='employees'
    )

    objects = EmployeeQuerySet.as_manager()

    class Meta:
        ordering = ('id',)
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.full_name
