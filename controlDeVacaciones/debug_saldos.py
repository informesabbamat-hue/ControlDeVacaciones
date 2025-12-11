import os
import django
from datetime import date
from django.db.models import Sum

# Setup Django (if running standalone, though shell handles this usually)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controlDeVacaciones.settings')
# django.setup()

from gestion.models import SaldoVacaciones

current_year = date.today().year
print(f"--- Desglose de 'Días del Equipo' para el ciclo {current_year} ---")

saldos = SaldoVacaciones.objects.filter(ciclo=current_year).select_related('empleado')
total_sum = 0

print(f"{'Empleado':<30} | {'Días Disponibles'}")
print("-" * 50)

for saldo in saldos:
    disponible = saldo.total_disponible()
    total_sum += disponible
    print(f"{saldo.empleado.nombre} {saldo.empleado.apellido:<20} | {disponible}")

print("-" * 50)
print(f"{'TOTAL':<30} | {total_sum}")
