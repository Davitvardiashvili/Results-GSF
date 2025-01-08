from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import (
    # Auth
    ObtainAuthTokenView, LogoutView,
    # Core lookups
    SchoolListCreate, SchoolRetrieveUpdateDestroy,
    GenderListCreate, GenderRetrieveUpdateDestroy,
    DisciplineListCreate, DisciplineRetrieveUpdateDestroy,
    # Competitors
    CompetitorListCreate, CompetitorRetrieveUpdateDestroy,
    # Seasons & AgeGroups
    SeasonListCreate, SeasonRetrieveUpdateDestroy,
    AgeGroupListCreate, AgeGroupRetrieveUpdateDestroy,
    # Stages & CompetitionDays
    StageListCreate, StageRetrieveUpdateDestroy,
    CompetitionDayListCreate, CompetitionDayRetrieveUpdateDestroy,
    # Registrations (replacing Cart)
    RegistrationListCreate, RegistrationRetrieveUpdateDestroy,
    # Results (replacing old Results)
    ResultListCreate, ResultRetrieveUpdateDestroy,
    # Utility endpoints
    randomize_bib_numbers,
    SyncRegistrationToResultsView,  # if you’re still syncing registrations to results
    batch_sync_results,
    SearchResultsAPIView,
    download_excel, download_pdf, download_results_pdf, results_by_date, season_winners
)

schema_view = get_schema_view(
    openapi.Info(
        title="GSF Competition",
        default_version='v1',
        description="Your API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # ----------------------------
    # Authentication
    # ----------------------------
    path('api-token-auth/', ObtainAuthTokenView.as_view(), name='api_token_auth'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # ----------------------------
    # Core Lookups
    # ----------------------------
    path('school/', SchoolListCreate.as_view(), name='school'),
    path('school/<int:pk>/', SchoolRetrieveUpdateDestroy.as_view(), name='school-detail'),

    path('gender/', GenderListCreate.as_view(), name='gender'),
    path('gender/<int:pk>/', GenderRetrieveUpdateDestroy.as_view(), name='gender-detail'),

    path('discipline/', DisciplineListCreate.as_view(), name='discipline'),
    path('discipline/<int:pk>/', DisciplineRetrieveUpdateDestroy.as_view(), name='discipline-detail'),

    # ----------------------------
    # Competitors
    # ----------------------------
    path('competitor/', CompetitorListCreate.as_view(), name='competitor'),
    path('competitor/<int:pk>/', CompetitorRetrieveUpdateDestroy.as_view(), name='competitor-detail'),

    # ----------------------------
    # Seasons & AgeGroups
    # ----------------------------
    path('season/', SeasonListCreate.as_view(), name='season'),
    path('season/<int:pk>/', SeasonRetrieveUpdateDestroy.as_view(), name='season-detail'),

    path('age-group/', AgeGroupListCreate.as_view(), name='agegroup'),
    path('age-group/<int:pk>/', AgeGroupRetrieveUpdateDestroy.as_view(), name='agegroup-detail'),

    # ----------------------------
    # Stages & CompetitionDays
    # ----------------------------
    path('stage/', StageListCreate.as_view(), name='stage'),
    path('stage/<int:pk>/', StageRetrieveUpdateDestroy.as_view(), name='stage-detail'),

    path('competition-day/', CompetitionDayListCreate.as_view(), name='competitionday'),
    path('competition-day/<int:pk>/', CompetitionDayRetrieveUpdateDestroy.as_view(), name='competitionday-detail'),

    # ----------------------------
    # Registrations (replacing Cart)
    # ----------------------------
    path('registration/', RegistrationListCreate.as_view(), name='registration'),
    path('registration/<int:pk>/', RegistrationRetrieveUpdateDestroy.as_view(), name='registration-detail'),

    # ----------------------------
    # Results
    # ----------------------------
    path('results/', results_by_date, name='results-list'),
    path('results/<int:pk>/', ResultRetrieveUpdateDestroy.as_view(), name='results-detail'),

    # ----------------------------
    # Utility Endpoints
    # ----------------------------
    path('randomizer/', randomize_bib_numbers, name='randomize-bib'),
    path('sync-registrations/', SyncRegistrationToResultsView.as_view(), name='sync-registrations'),
    path('batch_sync_results/', batch_sync_results, name='batch-sync-results'),
    path('search-results/', SearchResultsAPIView.as_view(), name='search-results'),

    path('download_excel/', download_excel, name='download_excel'),
    path('download_pdf/', download_pdf, name='download_pdf'),
    path('download_results_pdf/', download_results_pdf, name='download_results_pdf'),

    path('season-winners/', season_winners, name='season-winners'),

    # ----------------------------
    # Swagger / Redoc
    # ----------------------------
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
]
