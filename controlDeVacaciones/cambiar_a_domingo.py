# -*- coding: utf-8 -*-
# Script para cambiar el inicio de semana a domingo

with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Cambiar el cálculo del inicio de semana
# Buscar la sección donde se calcula fecha_inicio
old_code = """        # 2. CALENDARIO ANUAL - Generar SEMANAS COMPLETAS del año (Lunes a Domingo)
        # Encontrar el lunes de la semana que contiene el 1 de enero
        primer_dia = date(anio_ciclo, 1, 1)
        dias_hasta_lunes = primer_dia.weekday()  # 0=Lunes, 6=Domingo
        
        # Retroceder hasta el lunes (puede ser del año anterior)
        fecha_inicio = primer_dia - timedelta(days=dias_hasta_lunes)"""

new_code = """        # 2. CALENDARIO ANUAL - Generar SEMANAS COMPLETAS del año (Domingo a Sábado)
        # Encontrar el domingo de la semana que contiene el 1 de enero
        primer_dia = date(anio_ciclo, 1, 1)
        dia_semana = primer_dia.weekday()  # 0=Lunes, 6=Domingo
        
        # Calcular días hasta el domingo anterior
        # Si es domingo (6), no retroceder. Si es lunes (0), retroceder 1 día, etc.
        dias_hasta_domingo = (dia_semana + 1) % 7
        
        # Retroceder hasta el domingo (puede ser del año anterior)
        fecha_inicio = primer_dia - timedelta(days=dias_hasta_domingo)"""

content = content.replace(old_code, new_code)

# También cambiar el comentario en la creación de semana
content = content.replace(
    "# Crear semana de 7 días (Lunes a Domingo)",
    "# Crear semana de 7 días (Domingo a Sábado)"
)

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Calendario cambiado a semanas de Domingo a Sábado!")
