from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Client, ClientPayment
from .serializers import ClientSerializer, ClientPaymentSerializer


class IsActiveOfficeUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.is_active_subscriber and
                request.user.subscription_type == 'office')


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsActiveOfficeUser]

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='mark-as-paid')
    def mark_as_paid(self, request, pk=None):
        client = self.get_object()
        due = client.due_amount
        if due > 0:
            ClientPayment.objects.create(
                client=client,
                amount=due,
                note="Full payment marked as paid from dashboard"
            )
        serializer = self.get_serializer(client)
        return Response(serializer.data)


class ClientPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = ClientPaymentSerializer
    permission_classes = [IsActiveOfficeUser]

    def get_queryset(self):
        return ClientPayment.objects.filter(client__owner=self.request.user)
