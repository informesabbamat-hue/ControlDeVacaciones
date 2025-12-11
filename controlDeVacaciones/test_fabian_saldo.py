import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controlDeVacaciones.settings')
django.setup()

from gestion.models import SaldoVacaciones, Empleado

# Buscar a Fabian Caceres
try:
    empleado = Empleado.objects.get(apellido__icontains='Caceres', nombre__icontains='Fabian')
    print(f"OK Empleado encontrado: {empleado}")
    
    # Buscar saldos disponibles
    saldos = SaldoVacaciones.objects.filter(empleado=empleado)
    print(f"\nSaldos encontrados: {saldos.count()}")
    for s in saldos:
        print(f"  - Ciclo {s.ciclo}: iniciales={s.dias_iniciales}, adicionales={s.dias_adicionales}")
    
    # Obtener su saldo para 2026
    saldo = SaldoVacaciones.objects.get(empleado=empleado, ciclo=2026)
    
    print(f"\n--- DATOS DEL SALDO (2026) ---")
    print(f"Dias iniciales: {saldo.dias_iniciales}")
    print(f"Dias adicionales: {saldo.dias_adicionales}")
    print(f"Dias consumidos: {saldo.dias_consumidos_total()}")
    print(f"\n--- CALCULO MANUAL ---")
    
    dias_base_lct = empleado.dias_base_lct(2026)
    dias_acumulados = max(saldo.dias_iniciales, dias_base_lct)
    dias_adicionales = saldo.dias_adicionales or 0
    dias_consumidos = saldo.dias_consumidos_total()
    
    print(f"Dias base LCT: {dias_base_lct}")
    print(f"Dias acumulados (max): {dias_acumulados}")
    print(f"Dias adicionales: {dias_adicionales}")
    print(f"Total esperado: {dias_acumulados} + {dias_adicionales} - {dias_consumidos} = {dias_acumulados + dias_adicionales - dias_consumidos}")
    
    print(f"\n--- METODO total_disponible() ---")
    resultado = saldo.total_disponible()
    print(f"Resultado: {resultado}")
    
    esperado = dias_acumulados + dias_adicionales - dias_consumidos
    if resultado == esperado:
        print(f"\nOK CORRECTO! El metodo esta funcionando bien.")
        print(f"   Resultado: {resultado} = Esperado: {esperado}")
        print("\n*** DEBES REINICIAR EL SERVIDOR DJANGO ***")
        print("   El codigo esta correcto pero el servidor tiene la version vieja en memoria.")
    else:
        print(f"\nERROR: El metodo NO esta sumando los dias adicionales.")
        print(f"   Resultado: {resultado} != Esperado: {esperado}")
        
except Empleado.DoesNotExist:
    print("ERROR: No se encontro al empleado Fabian Caceres")
except SaldoVacaciones.DoesNotExist:
    print("ERROR: No se encontro el saldo para 2026")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
