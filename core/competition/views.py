from django.shortcuts import render,redirect
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.decorators import api_view,permission_classes
import random
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from django.db import IntegrityError



class ObtainAuthTokenView(APIView):
    throttle_classes = ()
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(
        operation_description="Post username and password to get an authentication token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
        ),
        responses={
            200: TokenSerializer,
            400: 'Invalid username/password'
        }
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout a user by invalidating the authentication token",
        responses={
            200: 'Successfully logged out',
            401: 'Unauthorized'
        }
    )
    def post(self, request, *args, **kwargs):
        # This will only succeed if the user is authenticated and has a valid token
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)




class SchoolListCreate(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    # Set different permissions for different request methods
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class SchoolRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated]


class CompetitorListCreate(generics.ListCreateAPIView):
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer
    # Set different permissions for different request methods
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]




class CompetitorRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer
    permission_classes = [IsAuthenticated]



class SeasonListCreate(generics.ListCreateAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    # Set different permissions for different request methods
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class SeasonRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    permission_classes = [IsAuthenticated]


class DisciplineListCreate(generics.ListCreateAPIView):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer
    # Set different permissions for different request methods
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class DisciplineRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer
    permission_classes = [IsAuthenticated]



class StageListCreate(generics.ListCreateAPIView):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    # Set different permissions for different request methods
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class StageRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    permission_classes = [IsAuthenticated]




class GroupListCreate(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # Set different permissions for different request methods
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class GroupRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]



class CartListCreate(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]


class CartRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

class ResultsListCreate(generics.ListCreateAPIView):
    queryset = Results.objects.all()
    serializer_class = ResultsSerializer
    # Set different permissions for different request methods
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class ResultsRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Results.objects.all()
    serializer_class = ResultsSerializer
    permission_classes = [IsAuthenticated]


@swagger_auto_schema(method='post', request_body=RandomizeBibNumbersSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def randomize_bib_numbers(request):
    # Parse and validate the request data using the serializer
    serializer = RandomizeBibNumbersSerializer(data=request.data)
    if serializer.is_valid():
        # Extract validated data from the serializer
        start_number = serializer.validated_data.get('start_number')
        ignore_numbers = serializer.validated_data.get('ignore_numbers', [])
        gender_id = serializer.validated_data.get('gender', None)
        stage_id = serializer.validated_data.get('stage',None)
        
        # Fetch carts based on the specified gender
        stage_ids = Group.objects.filter(stage_id=stage_id).values_list('id', flat=True)
        carts = Cart.objects.filter(group_id__in=stage_ids)

        group_ids = Group.objects.filter(gender_id=gender_id).values_list('id', flat=True)
        carts = carts.filter(group_id__in=group_ids)

        total_carts = carts.count()
        potential_numbers = set(range(start_number, start_number + total_carts + len(ignore_numbers))) - set(ignore_numbers)

        if len(potential_numbers) < total_carts:
            return Response({"error": "Not enough unique numbers available after excluding the ignored numbers."}, status=400)

        for cart in carts:
            cart.bib_number = random.choice(list(potential_numbers))
            potential_numbers.remove(cart.bib_number)
            cart.save()

        return Response({"message": "Bib numbers randomized successfully"})
    else:
        return Response(serializer.errors, status=400)





class SyncCartToResultsView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only admin users can access this endpoint

    @swagger_auto_schema(
        operation_description="Synchronize Cart entries to Results table",
        responses={
            200: 'Synchronization completed successfully',
            500: 'Internal Server Error'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            # Perform the synchronization
            sync_cart_to_results()
            return Response({"message": "Synchronization completed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error or handle it as needed
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def sync_cart_to_results():
    default_status, created = Status.objects.get_or_create(status='Active')

    for cart in Cart.objects.all():
        if cart.competitor:
            result_exists = Results.objects.filter(competitor=cart).exists()

            if not result_exists:
                try:
                    Results.objects.create(
                        competitor=cart,
                        status=default_status
                    )
                except IntegrityError as e:
                    # Handle the exception or log it
                    pass  # Replace with actual error handling