from django import template
from datetime import date

register = template.Library()

@register.filter(name='get_range_text')
def get_range_text(fechas_completas):
    """
    Toma una lista de objetos date (fechas_completas) y devuelve el texto del rango.
    Ej: [date(2025, 1, 1), ..., date(2025, 1, 7)] -> '1 al 7'
    Ej: [date(2025, 12, 29), ..., date(2026, 1, 4)] -> '29 al 4'
    
    Este filtro se aplica a 'semana.fechas_completas' en la plantilla.
    """
    if not fechas_completas:
        return ""
    
    # El primer objeto date de la lista (día de inicio de la semana)
    fecha_inicio = fechas_completas[0]
    
    # El último objeto date de la lista (día de fin de la semana)
    fecha_fin = fechas_completas[-1]
    
    # Caso para una semana incompleta (ej. la última semana del año con solo 1 día)
    if fecha_inicio.day == fecha_fin.day and len(fechas_completas) == 1:
        return f"{fecha_inicio.day}"
        
    # Devuelve el día de inicio y el día de fin. 
    # La cabecera del mes padre indica el mes de inicio.
    return f"{fecha_inicio.day} al {fecha_fin.day}"

@register.filter(name='add')
def add(value, arg):
    """Suma dos valores. Útil para el cálculo del colspan en el template."""
    try:
        # Intenta convertir ambos a enteros y sumarlos
        return int(value) + int(arg)
    except (ValueError, TypeError):
        # Si la conversión falla, devuelve el valor original
        return value