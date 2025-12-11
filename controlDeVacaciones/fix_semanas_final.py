# -*- coding: utf-8 -*-
# Script final para corregir generación de semanas completas

with open('gestion/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar la línea donde empieza la generación del calendario
start_idx = -1
for i, line in enumerate(lines):
    if '# 2. CALENDARIO ANUAL - Generar estructura de meses y SEMANAS' in line:
        start_idx = i
        break

if start_idx == -1:
    print("No se encontro la seccion del calendario")
    exit(1)

# Encontrar donde termina (antes de # 3. OBTENER EMPLEADOS)
end_idx = -1
for i in range(start_idx, len(lines)):
    if '# 3. OBTENER EMPLEADOS AGRUPADOS POR DEPARTAMENTO' in lines[i]:
        end_idx = i
        break

if end_idx == -1:
    print("No se encontro el final de la seccion")
    exit(1)

# Nuevo código para generación de semanas
nuevo_codigo = """        # 2. CALENDARIO ANUAL - Generar SEMANAS COMPLETAS del año (Lunes a Domingo)
        # Encontrar el lunes de la semana que contiene el 1 de enero
        primer_dia = date(anio_ciclo, 1, 1)
        dias_hasta_lunes = primer_dia.weekday()  # 0=Lunes, 6=Domingo
        
        # Retroceder hasta el lunes (puede ser del año anterior)
        fecha_inicio = primer_dia - timedelta(days=dias_hasta_lunes)
        
        # Generar todas las semanas del año
        todas_semanas = []
        fecha_actual = fecha_inicio
        
        # Continuar mientras la semana tenga al menos un día del año actual
        while True:
            # Crear semana de 7 días (Lunes a Domingo)
            semana = []
            for i in range(7):
                semana.append(fecha_actual + timedelta(days=i))
            
            # Verificar si esta semana tiene al menos un día del año actual
            tiene_dias_del_ano = any(dia.year == anio_ciclo for dia in semana)
            
            if not tiene_dias_del_ano and semana[0].year > anio_ciclo:
                break
            
            if tiene_dias_del_ano:
                # Determinar a qué mes asignar esta semana (mes con más días del año actual)
                meses_en_semana = {}
                for dia in semana:
                    if dia.year == anio_ciclo:
                        mes = dia.month
                        meses_en_semana[mes] = meses_en_semana.get(mes, 0) + 1
                
                if meses_en_semana:
                    mes_principal = max(meses_en_semana, key=meses_en_semana.get)
                    
                    # Formatear rango
                    inicio = semana[0]
                    fin = semana[6]
                    
                    if inicio.month == fin.month and inicio.year == fin.year:
                        rango = f"{inicio.day}-{fin.day}"
                    else:
                        rango = f"{inicio.day}/{inicio.month}-{fin.day}/{fin.month}"
                    
                    todas_semanas.append({
                        'dias': semana,
                        'inicio': inicio,
                        'fin': fin,
                        'mes': mes_principal,
                        'rango': rango
                    })
            
            fecha_actual += timedelta(days=7)
        
        # Agrupar semanas por mes
        meses_data = []
        for mes_num in range(1, 13):
            mes_nombre = MESES_ESPANOL.get(mes_num, f'Mes-{mes_num}')
            semanas_del_mes = [sem for sem in todas_semanas if sem['mes'] == mes_num]
            
            if semanas_del_mes:
                meses_data.append({
                    'numero': mes_num,
                    'nombre': mes_nombre,
                    'semanas': semanas_del_mes,
                    'total_semanas': len(semanas_del_mes)
                })

"""

# Reemplazar las líneas
new_lines = lines[:start_idx] + [nuevo_codigo] + lines[end_idx:]

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Generacion de semanas completas corregida!")
