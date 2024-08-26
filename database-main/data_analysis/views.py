from django.shortcuts import render, get_object_or_404
from .models import Order, OrderProduct
from django.core.paginator import Paginator
from datetime import timedelta, datetime
from django.utils import timezone  
from decimal import Decimal
from django.db.models import Sum, Count
from django.db.models import Q, F
from .forms import DateSelectorForm, DateRangeForm
from django.db.models.functions import Round


def home(request):
    # Retrieve all orders and order them by date, descending
    orders = Order.objects.all().order_by('-order_date')
    
    # Convert order_date to the local timezone for each order
    for order in orders:
        order.order_date = timezone.localtime(order.order_date)
    
    # Set up pagination, showing 20 orders per page
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Render the template with the paginated orders
    return render(request, 'home.html', {'orders': page_obj})


def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    products = OrderProduct.objects.filter(order=order)
    total_amount_with_shipping = order.total_amount + (order.shipping_cost or Decimal('0.00'))

    context = {
        'order': order,
        'products': products,
        'total_amount_with_shipping': total_amount_with_shipping,
        'shipping_method': order.shipping_method,
        'is_new_customer': order.is_new_customer,  # Nuevo campo
        'comments': order.comments,  # Comentario de la orden
    }
    return render(request, 'order_detail.html', context)


def stats_view(request):
    selected_date = None
    top_products = []
    daily_revenue = 0
    weekly_revenue = 0
    monthly_revenue = 0

    if request.method == 'POST':
        form = DateSelectorForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['selected_date']
            start_datetime = datetime.combine(selected_date, datetime.min.time())
            end_datetime = datetime.combine(selected_date, datetime.max.time())

            # Obtener los productos vendidos en la fecha seleccionada
            top_products = (
                OrderProduct.objects
                .exclude(product__description__icontains="Therapeutengutschein") 
                .exclude(product__description__icontains="Karton")
                .exclude(Q(product__description__icontains="PF42") | Q(product__description__icontains="CHV26") | Q(product__description__icontains="CAD38") | Q(product__description__icontains="CAD09A") | Q(product__description__icontains="CAS06") | Q(product__description__icontains="CAD13E") | Q(product__description__icontains="CHA60") | Q(product__description__icontains="PFD50") | Q(product__description__icontains="Standbodenbeutel"))
                .filter(order__order_date__range=[start_datetime, end_datetime])
                .values('product__description')
                .annotate(
                    total_quantity=Sum('quantity'),
                    total_revenue=Sum(F('quantity') * F('net_price'))
                )
                .order_by('-total_quantity')
            )

            # Redondear después de obtener los resultados
            top_products = [
                {
                    'product__description': product['product__description'],
                    'total_quantity': product['total_quantity'],
                    'total_revenue': round(product['total_revenue'], 2)
                }
                for product in top_products
            ]

            # Calcular el ingreso total en la fecha seleccionada
            daily_revenue = Order.objects.filter(order_date__range=[start_datetime, end_datetime]).aggregate(total_revenue=Sum('total_amount'))['total_revenue']
            daily_revenue = round(daily_revenue) if daily_revenue else 0
    else:
        form = DateSelectorForm()

        # Si no se ha seleccionado ninguna fecha, mostrar las estadísticas generales
        top_products = (
            OrderProduct.objects
            .exclude(product__description__icontains="Therapeutengutschein") 
            .exclude(product__description__icontains="Karton")
            .exclude(Q(product__description__icontains="PF42") | Q(product__description__icontains="CHV26") | Q(product__description__icontains="CAD38") | Q(product__description__icontains="CAD09A") | Q(product__description__icontains="CAS06") | Q(product__description__icontains="CAD13E") | Q(product__description__icontains="CHA60") | Q(product__description__icontains="PFD50") | Q(product__description__icontains="Standbodenbeutel"))
            .values('product__description')
            .annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('net_price'))
            )
            .order_by('-total_quantity')[:20]
        )

        # Redondear después de obtener los resultados
        top_products = [
            {
                'product__description': product['product__description'],
                'total_quantity': product['total_quantity'],
                'total_revenue': round(product['total_revenue'], 2)
            }
            for product in top_products
        ]

        # Calcular el ingreso total por semana
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        weekly_revenue = Order.objects.filter(order_date__range=[start_date, end_date]).aggregate(total_revenue=Sum('total_amount'))['total_revenue']

        # Calcular el ingreso total por mes
        start_date = end_date - timedelta(days=30)
        monthly_revenue = Order.objects.filter(order_date__range=[start_date, end_date]).aggregate(total_revenue=Sum('total_amount'))['total_revenue']

        # Redondear los ingresos a enteros
        weekly_revenue = round(weekly_revenue) if weekly_revenue else 0
        monthly_revenue = round(monthly_revenue) if monthly_revenue else 0

    context = {
        'form': form,
        'selected_date': selected_date,
        'top_products': top_products,
        'daily_revenue': daily_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
    }

    return render(request, 'stats.html', context)




def box_usage_view(request):
    form = DateRangeForm()
    box_products = []

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())

            # Filtrar y sumar el uso de las cajas dentro del rango de fechas seleccionado
            box_products = (
                OrderProduct.objects
                .filter(
                    Q(product__description__icontains="Karton") | 
                    Q(product__description__icontains="PF42") | 
                    Q(product__description__icontains="CHV26") | 
                    Q(product__description__icontains="CAS06") | 
                    Q(product__description__icontains="CAD13E") | 
                    Q(product__description__icontains="CHA60") | 
                    Q(product__description__icontains="PFD50") | 
                    Q(product__description__icontains="CAD09A") |
                    Q(product__description__icontains="CAD38") | 
                    Q(product__description__icontains="Standbodenbeutel")
                )
                .filter(order__order_date__range=[start_datetime, end_datetime])
                .values('product__description')
                .annotate(total_used=Sum('quantity'))
                .order_by('-total_used')
            )
    
    context = {
        'form': form,
        'box_products': box_products,
    }

    return render(request, 'box_usage.html', context)

