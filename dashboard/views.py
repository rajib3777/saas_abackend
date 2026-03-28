from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count
from django.utils import timezone
from employees.models import Employee, AttendanceRecord
from office.models import Client
from shop.models import Product, Sale, Parcel, AdCampaign


class IsActiveSubscriber(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active_subscriber


class DashboardView(APIView):
    permission_classes = [IsActiveSubscriber]

    def get(self, request):
        user = request.user
        now = timezone.now()
        month = now.month
        year = now.year

        data = {
            'subscription_type': user.subscription_type,
            'business_name': user.business_name,
        }

        # Common: Employee stats
        employees = Employee.objects.filter(owner=user, is_active=True)
        total_salary = employees.aggregate(total=Sum('monthly_salary'))['total'] or 0
        data['employees'] = {
            'total': employees.count(),
            'total_monthly_salary': float(total_salary),
            'total_yearly_salary': float(total_salary * 12),
        }

        if user.subscription_type == 'office':
            clients = Client.objects.filter(owner=user)
            total_income = clients.aggregate(t=Sum('paid_amount'))['t'] or 0
            total_due = sum(c.due_amount for c in clients)

            # 12-Month Chart Data for Office
            from office.models import ClientPayment
            import calendar
            chart_labels = []
            chart_income = []
            for i in range(-11, 1):
                target_month = month + i
                target_year = year
                while target_month < 1:
                    target_month += 12
                    target_year -= 1
                
                payments = ClientPayment.objects.filter(
                    client__owner=user, 
                    date__year=target_year, 
                    date__month=target_month
                )
                m_income = payments.aggregate(s=Sum('amount'))['s'] or 0
                
                chart_labels.append(f"{calendar.month_abbr[target_month]} {target_year}")
                chart_income.append(float(m_income))

            data['office'] = {
                'total_clients': clients.count(),
                'total_income': float(total_income),
                'total_due': float(total_due),
                'chart': {
                    'labels': chart_labels,
                    'income': chart_income,
                }
            }

        elif user.subscription_type == 'shop':
            # Sales this month
            sales = Sale.objects.filter(product__owner=user, date__month=month, date__year=year)
            total_revenue = sum(s.selling_price * s.quantity for s in sales)
            total_cost = sum(s.buying_price * s.quantity for s in sales)
            total_profit = total_revenue - total_cost

            # Parcels
            parcels = Parcel.objects.filter(owner=user)
            delivered = parcels.filter(status='delivered').count()
            returned = parcels.filter(status='returned').count()

            # Products
            products = Product.objects.filter(owner=user)
            low_stock = products.filter(stock__lt=5).count()

            # Ad Campaigns
            ads = AdCampaign.objects.filter(owner=user)
            total_ad_spend = ads.aggregate(s=Sum('total_spend'))['s'] or 0
            total_ad_revenue = ads.aggregate(r=Sum('revenue'))['r'] or 0

            # Sales all time
            all_sales = Sale.objects.filter(product__owner=user)
            all_time_revenue = sum(s.selling_price * s.quantity for s in all_sales)
            all_time_cost = sum(s.buying_price * s.quantity for s in all_sales)
            all_time_profit = all_time_revenue - all_time_cost

            # Rolling 9-Month Chart Data
            import calendar
            chart_labels = []
            chart_profit = []
            chart_revenue = []
            for i in range(-8, 4):
                target_month = month + i
                target_year = year
                while target_month < 1:
                    target_month += 12
                    target_year -= 1
                while target_month > 12:
                    target_month -= 12
                    target_year += 1

                monthly_sales = Sale.objects.filter(product__owner=user, date__year=target_year, date__month=target_month)
                m_rev = sum(s.selling_price * s.quantity for s in monthly_sales)
                m_cost = sum(s.buying_price * s.quantity for s in monthly_sales)
                
                chart_labels.append(f"{calendar.month_abbr[target_month]} {target_year}")
                chart_revenue.append(float(m_rev))
                chart_profit.append(float(m_rev - m_cost))

            data['shop'] = {
                'monthly_revenue': float(total_revenue),
                'monthly_cost': float(total_cost),
                'monthly_profit': float(total_profit),
                'all_time_revenue': float(all_time_revenue),
                'all_time_cost': float(all_time_cost),
                'all_time_profit': float(all_time_profit),
                'total_products': products.count(),
                'low_stock_products': low_stock,
                'total_parcels': parcels.count(),
                'delivered_parcels': delivered,
                'returned_parcels': returned,
                'total_ad_spend': float(total_ad_spend),
                'total_ad_revenue': float(total_ad_revenue),
                'chart': {
                    'labels': chart_labels,
                    'revenue': chart_revenue,
                    'profit': chart_profit
                }
            }

        return Response(data)


class SalesChartView(APIView):
    permission_classes = [IsActiveSubscriber]

    def get(self, request):
        user = request.user
        year = int(request.query_params.get('year', timezone.now().year))
        monthly_data = []
        for m in range(1, 13):
            sales = Sale.objects.filter(product__owner=user, date__year=year, date__month=m)
            profit = sum((s.selling_price - s.buying_price) * s.quantity for s in sales)
            revenue = sum(s.selling_price * s.quantity for s in sales)
            monthly_data.append({'month': m, 'profit': float(profit), 'revenue': float(revenue)})
        return Response(monthly_data)
