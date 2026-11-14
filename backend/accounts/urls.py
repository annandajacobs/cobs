from django.urls import path

from .views import AccountListCreateView, AccountDetailView


urlpatterns = [
    path("", AccountListCreateView.as_view(), name="account-list-crate"),
    path("<int:pk>/", AccountDetailView.as_view(), name="account-detail"),
]