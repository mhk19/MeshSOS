from rest_framework.response import Response
from mainapp.serializers import UserProfileSerializer
from backend.settings import SECRET_KEY
from rest_framework import status
from mainapp.models import UserProfile
from functools import wraps
import jwt


def check_user(function):
    @wraps(function)
    def wrap(self, request, *args, **kwargs):
        try:
            token = request.headers["Authorization"].split(" ")[1]
        except KeyError:
            return Response(
                {"message": "Authentication required"}, status=status.HTTP_403_FORBIDDEN
            )
        try:
            decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(decoded_jwt, token, decoded_jwt["username"])
            user = UserProfileSerializer(
                UserProfile.objects.get(name=decoded_jwt["username"])
            ).data
        except Exception:
            return Response(
                {"message": "The token is corrupt or the user does not exist"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return function(self, request, *args, **kwargs)

    return wrap