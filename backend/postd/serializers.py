import models

class PostdSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Postd
        fields = '__all__'


class PostdDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Postd
        fields = '__all__'
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Register
        fields = '__all__'

        