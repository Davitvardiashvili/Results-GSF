from django.urls import re_path, include,path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

schema_view = get_schema_view(
    openapi.Info(
        title="GSF Competition",
        default_version='v1',
        description="Your API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.com"),
        license=openapi.License(name="BSD License"),
        # Define security settings within the openapi.Info
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    # The security scheme is defined outside of the openapi.Info
)


urlpatterns = [
    path('school/', SchoolListCreate.as_view(), name='school'),
    path('school/<int:pk>/', SchoolRetrieveUpdateDestroy.as_view(), name='school-detail'),
    path('competitor/', CompetitorListCreate.as_view(), name='competitor'),
    path('competitor/<int:pk>/', CompetitorRetrieveUpdateDestroy.as_view(), name='competitor-detail'),
    path('season/', SeasonListCreate.as_view(), name='season'),
    path('season/<int:pk>/', SeasonRetrieveUpdateDestroy.as_view(), name='season-detail'),
    path('discipline/', DisciplineListCreate.as_view(), name='discipline'),
    path('discipline/<int:pk>/', DisciplineRetrieveUpdateDestroy.as_view(), name='discipline-detail'),
    path('competition/', CompetitionDayCreate.as_view(), name='competition'),
    path('competition/<int:pk>/', CompetitionDayRetrieveUpdateDestroy.as_view(), name='competition-detail'),
    path('stage/', StageListCreate.as_view(), name='stage'),
    path('stage/<int:pk>/', StageRetrieveUpdateDestroy.as_view(), name='stage-detail'),
    path('group/', GroupListCreate.as_view(), name='group'),
    path('group/<int:pk>/', GroupRetrieveUpdateDestroy.as_view(), name='group-detail'),
    path('cart/', CartListCreate.as_view(), name='cart'),
    path('cart/<int:pk>/', CartRetrieveUpdateDestroy.as_view(), name='cart-detail'),
    path('results/', ResultsListCreate.as_view(), name='results'),
    path('results/<int:pk>/', ResultsRetrieveUpdateDestroy.as_view(), name='results-detail'),
    path('randomizer/', randomize_bib_numbers, name='randomize-bib'),
    path('api-token-auth/', ObtainAuthTokenView.as_view(), name='api_token_auth'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('sync/', SyncCartToResultsView.as_view(), name='sync'),
    path('download_excel/', download_excel, name='download_excel'),
    path('batch_sync_results/', batch_sync_results, name='batch-sync-results'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]