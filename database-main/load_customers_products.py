import os
import django
from dotenv import load_dotenv
from load_data import connect_to_sql_server

# Configuración de Django
load_dotenv(dotenv_path='C:/Users/leoal/Desktop/databasework/database-main/.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database.settings')
django.setup()

from data_analysis.models import Customer, Product
from django.db import IntegrityError

def load_customers(cursor):
    query = """
    SELECT 
        k.kKunde AS customer_id, 
        a.cMail AS email, 
        a.cISO AS country,
        a.cVorname AS first_name,
        a.cName AS last_name,
        a.cPLZ AS postal_code,
        a.cStrasse AS street,
        a.cOrt AS city,
        a.cLand AS country,
        a.cTel AS phone
    FROM dbo.tKunde k
    LEFT JOIN dbo.tAdresse a ON k.kKunde = a.kKunde
    GROUP BY k.kKunde, a.cMail, a.cISO, a.cVorname, a.cName, a.cPLZ, a.cStrasse, a.cOrt, a.cLand, a.cTel
    """
    cursor.execute(query)
    for row in cursor:
        Customer.objects.update_or_create(
            customer_id=row.customer_id,
            defaults={
                'email': row.email,
                'first_name': row.first_name,
                'last_name': row.last_name,
                'postal_code': row.postal_code,
                'street': row.street,
                'city': row.city,
                'country': row.country,
                'phone': row.phone,
            }
        )

def load_products(cursor):
    query = """
    SELECT DISTINCT
        sa.kArtikel AS product_id,
        sa.cArtNr AS product_number,
        sa.cName AS description,
        sa.fVKNetto AS price
    FROM [eazybusiness].[dbo].[vStandardArtikel] sa
    WHERE sa.cArtNr IS NOT NULL AND sa.cArtNr != ''
    GROUP BY sa.kArtikel, sa.cArtNr, sa.cName, sa.fVKNetto

    """
    
    cursor.execute(query)

    for row in cursor.fetchall():
        # Ignora registros donde product_number es NULL o vacío
        if not row.product_number:
            print(f"Skipping non-product entry with ID {row.product_id} (likely shipping info).")
            continue

        try:
            Product.objects.update_or_create(
                product_id=row.product_id,
                defaults={
                    'product_number': row.product_number,
                    'description': row.description,
                    'price': row.price,
                }
            )
        except IntegrityError as e:
            print(f"Error inserting product {row.product_number}: {e}")

def main():
    connection = connect_to_sql_server()
    if connection is None:
        print("Connection to SQL Server failed.")
        return
    
    cursor = connection.cursor()
    load_customers(cursor)
    load_products(cursor)
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
