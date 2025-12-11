# -*- coding: utf-8 -*-
# Script para corregir la generación de semanas completas

with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar la sección de generación de calendario
old_section = """        # 2. CALENDARIO ANUAL - Generar estructura de meses y SEMANAS
        meses_data = []
        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        
        for mes_num in range(1, 13):
            mes_nombre = MESES_ESPANOL.get(mes_num, f'Mes-{mes_num}')
            
            # Obtener todas las semanas del mes
            semanas_del_mes = cal.monthdatescalendar(anio_ciclo, mes_num)
            
            # Procesar cada semana
            semanas_procesadas = []
            for semana in semanas_del_mes:
                # Filtrar solo días del mes actual
                dias_del_mes = [dia for dia in semana if dia.month == mes_num]
                
                if dias_del_mes:
                    semanas_procesadas.append({
                        'dias': dias_del_mes,
                        'inicio': dias_del_mes[0],
                        'fin': dias_del_mes[-1],
                        'rango': f\"{dias_del_mes[0].day}-{dias_del_mes[-1].day}\"
                    })
            
            meses_data.append({
                'numero': mes_num,
                'nombre': mes_nombre,
                'semanas': semanas_procesadas,
                'total_semanas': len(semanas_procesadas)
            })"""

new_section = """        # 2. CALENDARIO ANUAL - Generar SEMANAS COMPLETAS del año
        # Encontrar el primer lunes del año (o el lunes anterior al 1 de enero)
        primer_dia = date(anio_ciclo, 1, 1)
        dias_hasta_lunes = primer_dia.weekday()  # 0=Lunes, 6=Domingo
        
        if dias_hasta_lunes != 0:
            fecha_inicio = primer_dia - timedelta(days=dias_hasta_lunes)
        else:
            fecha_inicio = primer_dia
        
        # Generar todas las semanas del año
        todas_semanas = []
        fecha_actual = fecha_inicio
        
        while fecha_actual.year <= anio_ciclo:
            # Crear semana de 7 días (Lunes a Domingo)
            semana = []
            for i in range(7):
                semana.append(fecha_actual + timedelta(days=i))
            
            # Determinar a qué mes pertenece esta semana (mes del primer día)
            mes_semana = semana[0].month
            ano_semana = semana[0].year
            
            # Solo incluir semanas que empiezan en el año actual o antes del 7 de enero del siguiente
            if ano_semana == anio_ciclo or (ano_semana == anio_ciclo + 1 and mes_semana == 1 and semana[0].day <= 7):
                todas_semanas.append({
                    'dias': semana,
                    'inicio': semana[0],
                    'fin': semana[6],
                    'mes': mes_semana if ano_semana == anio_ciclo else 1,
                    'ano': ano_semana
                })
            
            fecha_actual += timedelta(days=7)
            
            # Detener si ya pasamos mucho del año siguiente
            if fecha_actual.year > anio_ciclo and fecha_actual.month > 1:
                break
        
        # Agrupar semanas por mes
        meses_data = []
        for mes_num in range(1, 13):
            mes_nombre = MESES_ESPANOL.get(mes_num, f'Mes-{mes_num}')
            
            # Filtrar semanas que pertenecen a este mes
            semanas_del_mes = []
            for sem in todas_semanas:
                if sem['mes'] == mes_num and sem['ano'] == anio_ciclo:
                    # Formatear rango
                    inicio = sem['inicio']
                    fin = sem['fin']
                    
                    if inicio.month == fin.month:
                        rango = f\"{inicio.day}-{fin.day}\"
                    else:
                        rango = f\"{inicio.day}/{inicio.month}-{fin.day}/{fin.month}\"
                    
                    semanas_del_mes.append({
                        'dias': sem['dias'],
                        'inicio': inicio,
                        'fin': fin,
                        'rango': rango
                    })
            
            if semanas_del_mes:
                meses_data.append({
                    'numero': mes_num,
                    'nombre': mes_nombre,
                    'semanas': semanas_del_mes,
                    'total_semanas': len(semanas_del_mes)
                })"""

content = content.replace(old_section, new_section)
print("Generacion de semanas completas actualizada")

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Archivo guardado!")
