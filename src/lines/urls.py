from django.urls import path, include

from rest_framework.routers import DefaultRouter

from lines import views

router = DefaultRouter()
router.register(r"scripts", views.ScriptsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("accounts/", include("drf_registration.urls")),
]
