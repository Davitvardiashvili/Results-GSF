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
import pandas as pd
from django.http import HttpResponse
from django.db.models import Prefetch
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
import os
from django.conf import settings
from reportlab.lib.units import inch


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


class CompetitionDayCreate(generics.ListCreateAPIView):
    queryset = CompetitionDay.objects.all()
    serializer_class = CompetitionDaySerializer
    # Set different permissions for different request methods
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class CompetitionDayRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompetitionDay.objects.all()
    serializer_class = CompetitionDaySerializer
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
    # Set different permissions for different request methods
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


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



class SearchResultsAPIView(generics.ListAPIView):
    serializer_class = ResultsSerializer

    def get_queryset(self):
        queryset = Results.objects.all()
        season = self.request.query_params.get('season')
        stage = self.request.query_params.get('stage')
        discipline = self.request.query_params.get('discipline')
        if season and stage and discipline:
            queryset = queryset.filter(season_name=season, stage_name=stage, discipline_name=discipline)
        return queryset
    

    

@swagger_auto_schema(method='post', request_body=RandomizeBibNumbersSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def randomize_bib_numbers(request):
    serializer = RandomizeBibNumbersSerializer(data=request.data)
    if serializer.is_valid():
        start_number = serializer.validated_data.get('start_number')
        ignore_numbers = serializer.validated_data.get('ignore_numbers', [])
        competition_id = serializer.validated_data.get('competition', None)
        gender_id = serializer.validated_data.get('gender', None)

        # Fetch all groups for the specified competition and gender
        groups = Group.objects.filter(competition_id=competition_id, gender_id=gender_id)

        # Loop through each group to randomize bib numbers
        for group in groups:
            # Fetch carts for the current group
            carts = Cart.objects.filter(group=group)
            # Calculate the total number of carts in the group
            total_carts = carts.count()

            # Generate potential numbers for the current group
            potential_numbers = set(range(start_number, start_number + total_carts))

            # Check if there is an overlap between potential numbers and ignored numbers
            if any(num in potential_numbers for num in ignore_numbers):
                # Extend the potential range until there is no overlap
                potential_numbers = set(range(start_number, start_number + total_carts + len(ignore_numbers)))


            try:
                start_number = max(potential_numbers) + 1
            except:
                print("no more groups")
            # Remove ignored numbers from potential numbers
            potential_numbers -= set(ignore_numbers)

            # Check if there are enough unique numbers available
            if len(potential_numbers) < total_carts:
                return Response({"error": "Not enough unique numbers available after excluding the ignored numbers."}, status=400)

            # Randomize bib numbers for carts in the current group
            for cart in carts:
                cart.bib_number = random.choice(list(potential_numbers))
                potential_numbers.remove(cart.bib_number)
                cart.save()

            # Update start_number for the next grou

        return Response({"message": "Bib numbers randomized successfully"})
    else:
        return Response(serializer.errors, status=400)








def create_result_for_cart(cart_id):

    try:
        cart = Cart.objects.get(pk=cart_id)
        result_exists = Results.objects.filter(competitor=cart).exists()

        if not result_exists:
            Results.objects.create(
                competitor=cart,
                competitor_info={"name":cart.competitor.name,
                                 "surname":cart.competitor.surname,
                                 "school":cart.competitor.school.school_name,
                                 "year":cart.competitor.year,
                                 "gender":cart.competitor.gender.id},
                group=cart.group,
                group_name=cart.group.group_name,
                stage_name=cart.group.competition.stage.name,
                season=cart.group.competition.stage.season,
                season_name=cart.group.competition.stage.season.season,
                discipline=cart.group.competition.discipline,
                discipline_name=cart.group.competition.discipline.discipline,
                competition=cart.group.competition,
                bib_number=cart.bib_number,
                stage=cart.group.competition.stage
            )
        else:
            # If a result already exists, you may want to handle this case accordingly
            pass

    except Cart.DoesNotExist:
        return Response({"error": f"Cart with ID {cart_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
    except IntegrityError:
        return Response({"error": f"Error creating result for Cart ID {cart_id}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": f"Result added successfully for Cart ID {cart_id}"}, status=status.HTTP_200_OK)







@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_sync_results(request):
    cart_ids = request.data.get('cart_ids', [])
    print("avoieeeee")

    # Iterate over cart IDs and create results
    for cart_id in cart_ids:
        create_result_for_cart(cart_id)

    return Response({"message": "Results added successfully"})




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
    print("aeeee")
    for cart in Cart.objects.all():
        if cart.competitor:
            result_exists = Results.objects.filter(competitor=cart).exists()


            if not result_exists:
                try:
                    Results.objects.create(
                        competitor=cart
                    )
                except IntegrityError as e:
                    # Handle the exception or log it
                    pass  # Replace with actual error handling

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def download_excel(request):
    if request.method == 'POST':
        cart_ids = request.data.get('cartIds', [])

        groups_with_carts = Group.objects.prefetch_related(
            Prefetch('cart_set', queryset=Cart.objects.filter(id__in=cart_ids).order_by('bib_number'), to_attr='sorted_carts')
        ).filter(cart__id__in=cart_ids).distinct().order_by('id')

        # List to hold all the DataFrames
        dfs = []
        bold_font = Font(bold=True)  # Create a Font object with bold text
        sky_blue_fill = PatternFill(start_color='00B0F0', end_color='00B0F0', fill_type='solid')  # Sky blue fill

        for group in groups_with_carts:
            # Add a row with the group name
            group_name_row = pd.DataFrame([{'BIB': 'Group:', 'Name': group.group_name}])
            dfs.append(group_name_row)

            # Add the data for each group
            group_data = [{
                'BIB': cart.bib_number,
                'Name': f'{cart.competitor.name} {cart.competitor.surname}',
                'Gender': cart.competitor.gender,
                'Year': cart.competitor.year,
                'School': cart.competitor.school.school_name
            } for cart in group.sorted_carts]

            group_df = pd.DataFrame(group_data)
            dfs.append(group_df)

        # Concatenate all DataFrames
        all_data = pd.concat(dfs, ignore_index=True)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Competitors.xlsx"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            all_data.to_excel(writer, sheet_name='Competitors', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Competitors']

            # Apply bold font and sky blue background to group name rows
            for row in worksheet.iter_rows(min_row=1, max_col=2, max_row=worksheet.max_row):
                for cell in row:
                    if cell.value == 'Group:':
                        for cell in row:
                            cell.font = bold_font
                            cell.fill = sky_blue_fill

        return response
    return Response({"error": "Invalid request"}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def download_results_pdf(request):
    font_path = os.path.join(settings.BASE_DIR, 'competition/fonts', 'bpg_glaho_sylfaen.ttf')
    try:
        pdfmetrics.registerFont(TTFont('kartuli', font_path))
    except Exception as e:
        print(f"Failed to register font: {str(e)}")
        return Response({"error": f"Failed to register font: {str(e)}"}, status=500)



    def draw_header(canvas, doc):
        logo_path = os.path.join(settings.BASE_DIR, 'competition/fonts', 'GSF-Logo.png')  # Replace with your logo path
        logo = Image(logo_path, width=80, height=80)
        logo.drawOn(canvas, doc.leftMargin - 40, doc.height + doc.topMargin - 30)

        title = "საქართველოს ჩემპიონატი - სპეციალური სლალომი"
        title_style = ParagraphStyle(name='TitleStyle', fontSize=16, alignment=1)
        title_paragraph = Paragraph(title, title_style)
        title_paragraph.wrapOn(canvas, doc.width, doc.topMargin)
        title_paragraph.drawOn(canvas, doc.width /2 - 160, doc.height + doc.topMargin)

        # date_text = "Date: " + str(datetime.now().strftime('%Y-%m-%d'))
        date_text = "Date: " + '2024-04-12'
        date_paragraph = Paragraph(date_text, title_style)
        date_paragraph.wrapOn(canvas, doc.width, doc.topMargin)
        date_paragraph.drawOn(canvas, doc.width - doc.rightMargin - 110, doc.height + doc.topMargin)

    if request.method == 'POST':
        results_ids = request.data.get('resultIds', [])

    # Fetch results based on the order specified by the frontend
        results_data = Results.objects.filter(id__in=results_ids)
        results_data_dict = {result.id: result for result in results_data}

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Results.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter, topMargin=1.5*inch)
        elements = []

        sky_color = colors.HexColor('#2F89D0')
        sand_color = colors.HexColor('#b0caff')

        page_width, page_height = letter
        table_width = page_width * 0.9  # 80% of the page width
        column_widths = [table_width / 20, table_width / 20, table_width / 4, table_width / 10, table_width / 16, table_width / 16, table_width / 8]

        groups_with_results = Group.objects.filter(cart__results__id__in=results_ids).distinct().order_by('id')

        for group in groups_with_results:
            # Your existing code for drawing the header and table for each group
            group_name_data = [[group.group_name]]
            group_name_table = Table(group_name_data, colWidths=[table_width])
            group_name_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), sky_color),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 0), (-1, -1), 'kartuli', 12),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ])
            group_name_table.setStyle(group_name_style)
            elements.append(group_name_table)
            elements.append(Spacer(1, 12))

            data = [['Rank', 'BIB', 'სპორტსმენი', 'სკოლა', 'წელი', 'სქესი', 'დრო1', 'დრო2', 'ჯამური დრო']]

            # Use the result IDs specified by the frontend and filter for each group
            for result_id in results_ids:
                result = results_data_dict.get(result_id)
                if result and result.competitor.group == group:
                    data.append([
                        result.place,
                        result.competitor.bib_number,
                        f'{result.competitor.competitor.name} {result.competitor.competitor.surname}',
                        result.competitor.competitor.school.school_name,
                        result.competitor.competitor.year,
                        result.competitor.competitor.gender,
                        result.run1,
                        result.run2,
                        result.run_total
                    ])

            data_table = Table(data, colWidths=column_widths)
            data_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), sand_color),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONT', (0, 0), (-1, -1), 'kartuli', 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])
            data_table.setStyle(data_style)
            elements.append(data_table)
            elements.append(Spacer(1, 12))

        doc.build(elements, onFirstPage=draw_header)

        return response

    return Response({"error": "Invalid request"}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def download_pdf(request):
    font_path = os.path.join(settings.BASE_DIR, 'competition/fonts', 'bpg_glaho_sylfaen.ttf')
    try:
        pdfmetrics.registerFont(TTFont('kartuli', font_path))
    except Exception as e:
        return Response({"error": f"Failed to register font: {str(e)}"}, status=500)

    def draw_header(canvas, doc):
        logo_path = os.path.join(settings.BASE_DIR, 'competition/fonts', 'GSF-Logo.png')  # Replace with your logo path
        logo = Image(logo_path, width=80, height=80)
        logo.drawOn(canvas, doc.leftMargin - 40, doc.height + doc.topMargin - 30)

        title = "Start List"
        title_style = ParagraphStyle(name='TitleStyle', fontSize=16, alignment=1)
        title_paragraph = Paragraph(title, title_style)
        title_paragraph.wrapOn(canvas, doc.width, doc.topMargin)
        title_paragraph.drawOn(canvas, doc.width /2 - 160, doc.height + doc.topMargin)

        date_text = "Date: " + str(datetime.now().strftime('%Y-%m-%d'))
        date_paragraph = Paragraph(date_text, title_style)
        date_paragraph.wrapOn(canvas, doc.width, doc.topMargin)
        date_paragraph.drawOn(canvas, doc.width - doc.rightMargin - 110, doc.height + doc.topMargin)


    if request.method == 'POST':
        cart_ids = request.data.get('cartIds', [])
        groups_with_carts = Group.objects.prefetch_related(
            Prefetch('cart_set', queryset=Cart.objects.filter(id__in=cart_ids).order_by('bib_number'), to_attr='sorted_carts')
        ).filter(cart__id__in=cart_ids).distinct().order_by('id')


        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Start_list.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter, topMargin=1.5*inch)
        elements = []

        sky_color = colors.HexColor('#2F89D0')
        sand_color = colors.HexColor('#b0caff')

        page_width, page_height = letter
        table_width = page_width * 0.9  # 80% of the page width
        narrow_column_width = table_width / 10
        wide_column_width = (table_width - 3 * narrow_column_width) / 2
        column_widths = [table_width / 12, wide_column_width, narrow_column_width, narrow_column_width, wide_column_width]

        for group in groups_with_carts:
            # Group name header
            group_name_data = [[group.group_name]]
            group_name_table = Table(group_name_data, colWidths=[table_width])
            group_name_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), sky_color),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 0), (-1, -1), 'kartuli',12),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ])
            group_name_table.setStyle(group_name_style)
            elements.append(group_name_table)
            elements.append(Spacer(1, 12))

            # Data table
            data = [['BIB', 'სპორტსმენი', 'სქესი', 'წელი', 'სკოლა']]
            for cart in group.sorted_carts:
                data.append([
                    cart.bib_number,
                    f'{cart.competitor.name} {cart.competitor.surname}',
                    cart.competitor.gender,
                    cart.competitor.year,
                    cart.competitor.school.school_name
                ])

            data_table = Table(data, colWidths=column_widths)
            data_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), sand_color),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONT', (0, 0), (-1, -1), 'kartuli', 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])
            data_table.setStyle(data_style)
            elements.append(data_table)
            elements.append(Spacer(1, 12))

        doc.build(elements, onFirstPage=draw_header)

        return response

    return Response({"error": "Invalid request"}, status=400)