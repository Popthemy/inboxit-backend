from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import get_dashboard_metrics
from .serializers import DashboardMetricsSerializer
from .documentation.analytics.schemas import dashboard_metric_doc

class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class =DashboardMetricsSerializer

    @dashboard_metric_doc
    def get(self, request):
        qs = get_dashboard_metrics(request.user)
        data =DashboardMetricsSerializer(qs).data
        return Response(data)
