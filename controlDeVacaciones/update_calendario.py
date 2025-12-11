# -*- coding: utf-8 -*-
# Script para actualizar solo la función calendario_global

with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar la función calendario_global completa
old_function = """@login_required
def calendario_global(request):
    \"\"\"
    Vista que genera la tabla de planificación anual de vacaciones,
    agrupando las columnas por semanas (rangos de Lunes a Domingo).
    \"\"\"
    try:
        # 1. DEFINICIÓN DEL CICLO
        anio_ciclo = date.today().year

        # 2. CALENDARIO ANUAL (Prepara las columnas de la tabla: Mes/Semana)
        calendario_anual = {}
        # Inicializamos el calendario. setfirstweekday(calendar.MONDAY) asegura que
        # la semana empiece el Lunes (0) y termine el Domingo (6).
        cal = calendar.Calendar(firstweekday=calendar.MONDAY)

        # Iteramos de Enero (1) a Diciembre (12)
        for mes_num in range(1, 13):
            mes_nombre = MESES_ESPANOL.get(mes_num, 'NONE-')
            
            # monthdatescalendar() devuelve una lista de semanas, donde cada semana
            # es una lista de 7 objetos date, incluyendo días de meses vecinos.
            mes_por_semanas = cal.monthdatescalendar(anio_ciclo, mes_num)
            
            semanas_del_mes = []
            
            for semana in mes_por_semanas:
                dias_validos = [] # Días que realmente pertenecen al mes actual
                
                fecha_inicio = None
                fecha_fin = None
                
                for dia in semana:
                    # Solo consideramos los días que pertenecen al mes actual
                    if dia.month == mes_num:
                        dias_validos.append(dia)
                        
                        # Establecer la fecha de inicio y fin del rango (solo días del mes)
                        if fecha_inicio is None:
                            fecha_inicio = dia
                        fecha_fin = dia # La última fecha válida será la de fin

                # Si no hay días válidos en la semana (ej. semana 1 que es toda de Dic del año anterior)
                if not dias_validos:
                    continue

                # El rango de la semana se define con el primer día y el último día válido.
                rango_semanal = f\"{fecha_inicio.day} al {fecha_fin.day}\"

                # Agrupamos la semana
                semanas_del_mes.append({
                    'rango': rango_semanal,
                    'dias': dias_validos, # Lista de objetos date (7, 6 o menos)
                    'num_columnas': len(dias_validos), # Colspan para esta semana (5, 6 o 7)
                })

            calendario_anual[mes_nombre] = semanas_del_mes

        # 3. LISTA DE EMPLEADOS (Reemplaza esta simulación con tu consulta a la base de datos)
        empleados_planificacion = []
        for i in range(3):
            empleados_planificacion.append({
                'id': i + 1,
                'nombre': f'Empleado {i+1}',
                'apellido': 'Apellido',
                'dias_disponibles': 21
            })

        context = {
            'anio_ciclo': anio_ciclo,
            'calendario_anual': calendario_anual, # Nueva estructura de Semanas
            'empleados_planificacion': empleados_planificacion,
        }

        return render(request, 'gestion/planificacion_calendario.html', context)
        
    except Exception as e:
        print(f\"ERROR: {e}\")
        return render(request, 'gestion/error.html', {'error_message': str(e)})"""

new_function = """@login_required
def calendario_global(request):
    \"\"\"
    Vista que genera la tabla de planificación anual de vacaciones.
    Muestra empleados en filas y días del año en columnas.
    \"\"\"
    try:
        # 1. DEFINICIÓN DEL CICLO
        anio_ciclo = int(request.GET.get('anio', date.today().year))

        # 2. CALENDARIO ANUAL - Generar estructura de meses y días
        meses_data = []
        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        
        for mes_num in range(1, 13):
            mes_nombre = MESES_ESPANOL.get(mes_num, f'Mes-{mes_num}')
            
            # Obtener todas las semanas del mes
            semanas = cal.monthdatescalendar(anio_ciclo, mes_num)
            
            # Recolectar todos los días que pertenecen al mes actual
            dias_del_mes = []
            for semana in semanas:
                for dia in semana:
                    if dia.month == mes_num:
                        dias_del_mes.append(dia)
            
            meses_data.append({
                'numero': mes_num,
                'nombre': mes_nombre,
                'dias': dias_del_mes,
                'total_dias': len(dias_del_mes)
            })

        # 3. OBTENER TODOS LOS EMPLEADOS CON SUS DATOS
        empleados = Empleado.objects.all().select_related(
            'departamento', 
            'manager_aprobador'
        ).order_by('departamento__nombre', 'apellido', 'nombre')
        
        # 4. PREPARAR DATOS DE CADA EMPLEADO
        empleados_data = []
        for emp in empleados:
            # Obtener o crear saldo de vacaciones
            saldo, created = SaldoVacaciones.objects.get_or_create(
                empleado=emp,
                ciclo=anio_ciclo,
                defaults={'dias_iniciales': emp.dias_base_lct(anio_ciclo)}
            )
            
            # Obtener vacaciones aprobadas del año
            vacaciones = RegistroVacaciones.objects.filter(
                empleado=emp,
                estado=RegistroVacaciones.ESTADO_APROBADA,
                fecha_inicio__year=anio_ciclo
            )
            
            empleados_data.append({
                'empleado': emp,
                'departamento': emp.departamento.nombre if emp.departamento else 'Sin Departamento',
                'dias_disponibles': saldo.total_disponible(),
                'dias_tomados': saldo.dias_consumidos_total(),
                'dias_iniciales': saldo.dias_iniciales,
                'vacaciones': list(vacaciones),
            })

        context = {
            'anio_ciclo': anio_ciclo,
            'meses_data': meses_data,
            'empleados_data': empleados_data,
        }

        return render(request, 'gestion/calendario_global.html', context)
        
    except Exception as e:
        logger.error(f\"Error en calendario_global: {e}\")
        return render(request, 'gestion/error.html', {'error_message': str(e)})"""

content = content.replace(old_function, new_function)
print("Funcion calendario_global actualizada")

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Archivo guardado!")
