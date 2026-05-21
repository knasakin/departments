from rest_framework import serializers
from departments.models import Department, Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = (
            'id',
            'full_name',
            'position',
            'hired_at',
            'created_at',
        )


class DepartmentSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        source='parent',
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
        default=None
    )

    class Meta:
        model = Department
        fields = (
            'id',
            'name',
            'parent_id',
            'created_at',
        )
        validators = []

    def validate(self, attrs):
        parent = attrs.get('parent', getattr(self.instance, 'parent', None))
        name = attrs.get('name', getattr(self.instance, 'name', '')).strip()

        queryset = Department.objects.filter(parent=parent, name=name)
        if self.instance is not None:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError('В пределах одного parent названия должны быть уникальны')

        department = self.instance
        if department is None or parent is None:
            return attrs

        if parent.id == department.id:
            raise serializers.ValidationError('Нельзя сделать подразделение родителем самого себя')

        current_parent = parent
        while current_parent is not None:
            if current_parent.id == department.id:
                raise serializers.ValidationError('Нельзя создать цикл в дереве')

            current_parent = current_parent.parent

        return attrs

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Название не может быть пустым')

        return value


class DepartmentTreeSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = (
            'id',
            'name',
            'parent_id',
            'created_at',
            'employees',
            'children',
        )

    def get_employees(self, obj):
        include_employees = self.context.get('include_employees', True)
        if not include_employees:
            return []

        employees = obj.employees.all().order_by('created_at')
        return EmployeeSerializer(employees, many=True).data

    def get_children(self, obj):
        depth = self.context.get('depth', 1)
        if depth <= 0:
            return []

        children = obj.children.all()

        serializer = DepartmentTreeSerializer(
            children,
            many=True,
            context={
                **self.context,
                'depth': depth - 1,
            },
        )

        return serializer.data
