import os
import django
from datetime import date, timedelta
import sys

# Setup Django environment
sys.path.append('c:\\Sistemas ABBAMAT\\ControlDeVacaciones\\controlDeVacaciones')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controlDeVacaciones.settings')
django.setup()

from gestion.views import _generar_datos_anio, calendario_global
from django.test import RequestFactory

def test_logic():
    print("Testing _generar_datos_anio(2025)...")
    try:
        data = _generar_datos_anio(2025)
        print(f"Success! Generated {len(data['meses_data'])} months.")
    except Exception as e:
        print(f"Error in _generar_datos_anio: {e}")
        import traceback
        traceback.print_exc()

    print("\nTesting calendario_global view logic...")
    factory = RequestFactory()
    request = factory.get('/gestion/calendario_global/?anio=todos')
    request.user = None # Mock user if needed, but view has @login_required so we might need to mock that or bypass it.
    
    # Since we can't easily bypass @login_required without a user, let's just test the logic inside the view if possible,
    # or just trust the unit test of the helper function first.
    
    # Let's try to simulate the logic inside calendario_global manually
    try:
        anios_a_mostrar = [2024, 2025, 2026]
        meses_globales = []
        for anio in anios_a_mostrar:
            datos_anio = _generar_datos_anio(anio)
            anio_corto = str(anio)[-2:]
            for mes in datos_anio['meses_data']:
                mes['nombre'] = f"{mes['nombre']} {anio_corto}"
                meses_globales.append(mes)
        print(f"Success! Generated global months: {len(meses_globales)}")
    except Exception as e:
        print(f"Error in manual logic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logic()
