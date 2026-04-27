# analytics/urls.py

from django.urls import path
from .views import DashboardMetricsView

urlpatterns = [
    path("metrics/", DashboardMetricsView.as_view(), name="dashboard_metrics"),
]
