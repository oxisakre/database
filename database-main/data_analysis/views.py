from django.shortcuts import render, get_object_or_404
from .models import Order, OrderProduct
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta, datetime
from django.utils import timezone  
from decimal import Decimal
from django.db.models import Sum, Count
from django.db.models import Q, F
from .forms import DateSelectorForm, DateRangeForm
from django.db.models.functions import Round
from django.http import JsonResponse
from django.template.loader import render_to_string

def home(request):
    # Obtener el término de búsqueda del campo de búsqueda
    search_query = request.GET.get('search', '')

    # Filtrar órdenes por producto si se proporciona un término de búsqueda
    if search_query:
        # Filtrar órdenes que contienen el producto buscado en la descripción
        orders = Order.objects.filter(
            orderproduct__product__description__icontains=search_query
        ).distinct().order_by('-order_date')
    else:
        # Si no hay término de búsqueda, devolver todas las órdenes
        orders = Order.objects.all().order_by('-order_date')
    
    # Convertir order_date a la zona horaria local para cada orden
    for order in orders:
        order.order_date = timezone.localtime(order.order_date)
    
    # Paginación de las órdenes, mostrando 20 órdenes por página
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Renderizar la plantilla con las órdenes paginadas y el término de búsqueda
    return render(request, 'home.html', {'orders': page_obj, 'search_query': search_query})


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
    form = DateRangeForm(request.POST or None)
    top_products = []
    daily_revenue = weekly_revenue = monthly_revenue = 0
    platform_usage = []
    payment_methods = []

    # Fechas predeterminadas para el cálculo
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)
    products_per_page = 10  # Número inicial de productos por página

    if form.is_valid():
        # Rango de fechas seleccionado por el usuario
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Calcular ingresos para el rango de fechas seleccionado
        selected_revenue = Order.objects.filter(order_date__range=[start_datetime, end_datetime]).aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0
    else:
        # Rango de fechas predeterminado para la vista inicial
        start_datetime = one_month_ago
        end_datetime = today
        selected_revenue = Order.objects.filter(order_date__range=[today, today]).aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0

    # Obtener los productos vendidos en el rango de fechas seleccionado
    top_products = (
        OrderProduct.objects
        .filter(order__order_date__range=[start_datetime, end_datetime])
        .exclude(product__description__icontains="Therapeutengutschein") 
        .exclude(product__description__icontains="Karton")
        .exclude(Q(product__description__icontains="PF42") | Q(product__description__icontains="CHV26") | Q(product__description__icontains="CAD38") | Q(product__description__icontains="CAD09A") | Q(product__description__icontains="CAS06") | Q(product__description__icontains="CAD13E") | Q(product__description__icontains="CHA60") | Q(product__description__icontains="PFD50") | Q(product__description__startswith="TH") | Q(product__description__icontains="Standbodenbeutel"))
        .values('product__description')
        .annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('net_price'))
        )
        .order_by('-total_quantity')
    )

    # Paginación de productos
    paginator = Paginator(top_products, products_per_page)
    page = request.GET.get('page', 1)
    try:
        paginated_products = paginator.page(page)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    # Calcular ingresos semanales y mensuales
    weekly_revenue = Order.objects.filter(order_date__range=[one_week_ago, today]).aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0
    monthly_revenue = Order.objects.filter(order_date__range=[one_month_ago, today]).aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0

    # Usos de plataforma
    platform_usage = (
        Order.objects.filter(order_date__range=[start_datetime, end_datetime])
        .values('platform')
        .annotate(usage_count=Count('platform'))
        .order_by('-usage_count')
    )

    # Métodos de pago
    payment_methods = (
        Order.objects.filter(order_date__range=[start_datetime, end_datetime])
        .values('payment_method')
        .annotate(method_count=Count('payment_method'))
        .order_by('-method_count')
    )

    # Comprobamos si es una solicitud AJAX para cargar más productos
    if request.is_ajax():
        products_html = render_to_string('partial_top_products.html', {'top_products': paginated_products})
        return JsonResponse({'products_html': products_html})

    context = {
        'form': form,
        'top_products': paginated_products,
        'daily_revenue': selected_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'platform_usage': platform_usage,
        'payment_methods': payment_methods,
        'start_date': start_datetime.date(),
        'end_date': end_datetime.date(),
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

