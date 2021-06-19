from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from users.serializers import UserSerializer
from users.models import User

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print('is_live', getattr(request, 'is_live'))
        return super().get(request, *args, **kwargs)
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    





