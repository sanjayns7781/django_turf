"""""Serializer to handle the operations and all """
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .models import Role,User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

    
class RegisterSerializer(serializers.ModelSerializer):
    # to make the password not exposed we are overiding the defalt
    password =  serializers.CharField(write_only=True)
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), required=False
    )
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'phone_number', 'role']

    def create(self, validated_data):
        request = self.context.get('request')
        role = validated_data.pop('role',None)

        if not role:
            role = Role.objects.get(name="CUSTOMER")
        else:
            if role.name in ['ADMIN','OWNER']:
                if not request.user.is_authenticated or request.user.role.name != "ADMIN":
                    raise serializers.ValidationError("Only ADMIN can assign ADMIN/OWNER roles.")
                
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            role=role
        )

        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data['access_token'] = str(refresh.access_token)
        data['refresh_token'] = str(refresh)
        data['role'] = {
            "id": instance.role.id,
            "name": instance.role.name
        }
        return data

