import os
import django
from dotenv import load_dotenv

# Configuración de Django
load_dotenv(dotenv_path='C:/Users/leoal/Desktop/databasework/database-main/.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database.settings')
django.setup()

from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import IntegrityError
from data_analysis.models import Customer, Product, Order, OrderProduct
from load_data import connect_to_sql_server

def load_orders(cursor, start_date, end_date):
    query = """
        SELECT
            b.kBestellung AS order_id,
            b.cBestellNr AS order_number,
            b.dErstellt AS order_date,
            b.tKunde_kKunde AS customer_id,
            p.tArtikel_kArtikel AS product_id,
            p.cArtNr AS product_number,
            p.cString AS product_description,
            p.nAnzahl AS quantity,
            p.fVKNetto AS net_price,
            va.fPrice AS shipping_cost,
            va.cName AS shipping_method
        FROM dbo.tBestellung b
        JOIN dbo.tBestellPos p ON b.kBestellung = p.tBestellung_kBestellung
        LEFT JOIN dbo.tVersand v ON b.kBestellung = v.kVersand
        LEFT JOIN dbo.tVersandArt va ON v.kVersandArt = va.kVersandArt
        WHERE b.dErstellt BETWEEN CONVERT(datetime, ?, 120) AND CONVERT(datetime, ?, 120)
    """
    
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute(query, (start_date_str, end_date_str))

    orders_dict = {}

    for row in cursor.fetchall():
        order_number = row.order_number
        if order_number not in orders_dict:
            orders_dict[order_number] = {
                'customer_id': row.customer_id,
                'order_date': timezone.make_aware(row.order_date, timezone.get_default_timezone()),
                'shipping_cost': row.shipping_cost or Decimal('0.00'),
                'shipping_method': row.shipping_method or "None",
                'total_amount': Decimal('0.00'),
                'products': []
            }
        
        try:
            product = Product.objects.get(product_id=row.product_id)
        except Product.DoesNotExist:
            print(f"Product with ID {row.product_id} does not exist. Skipping order {order_number}.")
            continue

        orders_dict[order_number]['products'].append({
            'product': product,
            'quantity': row.quantity,
            'net_price': row.net_price
        })
        orders_dict[order_number]['total_amount'] += row.net_price * row.quantity
    
    for order_number, order_data in orders_dict.items():
        save_order(order_number, order_data)

def save_order(order_number, order_data):
    try:
        customer = Customer.objects.get(customer_id=order_data['customer_id'])
        
        # Verificar si 'order_date' ya tiene zona horaria
        order_date = order_data['order_date']
        if timezone.is_naive(order_date):
            order_date = timezone.make_aware(order_date, timezone.get_default_timezone())

        order, created = Order.objects.update_or_create(
            order_number=order_number,
            defaults={
                'customer': customer,
                'order_date': order_date,
                'total_amount': order_data['total_amount'] + order_data['shipping_cost'],
                'shipping_cost': order_data['shipping_cost'],
                'shipping_method': order_data['shipping_method']
            }
        )

        for product_data in order_data['products']:
            OrderProduct.objects.update_or_create(
                order=order,
                product=product_data['product'],
                defaults={
                    'quantity': product_data['quantity'],
                    'net_price': product_data['net_price']
                }
            )
    except Customer.DoesNotExist:
        print(f"Customer with ID {order_data['customer_id']} does not exist.")
    except IntegrityError as e:
        print(f"Error saving order {order_number}: {e}")
    
def main():
    connection = connect_to_sql_server()
    if connection is None:
        print("Connection to SQL Server failed.")
        return
    
    cursor = connection.cursor()

    end_date = timezone.now()
    start_date = end_date - timedelta(days=60)

    load_orders(cursor, start_date, end_date)
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
