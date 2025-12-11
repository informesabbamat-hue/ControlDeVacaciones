# -*- coding: utf-8 -*-
# Script para actualizar calendario_global con semanas y agrupación por departamento

with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar la función calendario_global
old_function = """@login_required
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

new_function = """@login_required
def calendario_global(request):
    \"\"\"
    Vista que genera la tabla de planificación anual de vacaciones.
    Muestra empleados agrupados por departamento y semanas del año en columnas.
    \"\"\"
    try:
        # 1. DEFINICIÓN DEL CICLO
        anio_ciclo = int(request.GET.get('anio', date.today().year))

        # 2. CALENDARIO ANUAL - Generar estructura de meses y SEMANAS
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
            })

        # 3. OBTENER EMPLEADOS AGRUPADOS POR DEPARTAMENTO
        departamentos = Departamento.objects.all().order_by('nombre')
        
        departamentos_data = []
        for depto in departamentos:
            empleados_depto = Empleado.objects.filter(
                departamento=depto
            ).select_related('manager_aprobador').order_by('apellido', 'nombre')
            
            empleados_list = []
            for emp in empleados_depto:
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
                
                empleados_list.append({
                    'empleado': emp,
                    'dias_disponibles': saldo.total_disponible(),
                    'dias_tomados': saldo.dias_consumidos_total(),
                    'vacaciones': list(vacaciones),
                })
            
            if empleados_list:  # Solo agregar departamentos con empleados
                departamentos_data.append({
                    'departamento': depto,
                    'empleados': empleados_list
                })
        
        # Empleados sin departamento
        empleados_sin_depto = Empleado.objects.filter(
            departamento__isnull=True
        ).select_related('manager_aprobador').order_by('apellido', 'nombre')
        
        if empleados_sin_depto.exists():
            empleados_list = []
            for emp in empleados_sin_depto:
                saldo, created = SaldoVacaciones.objects.get_or_create(
                    empleado=emp,
                    ciclo=anio_ciclo,
                    defaults={'dias_iniciales': emp.dias_base_lct(anio_ciclo)}
                )
                
                vacaciones = RegistroVacaciones.objects.filter(
                    empleado=emp,
                    estado=RegistroVacaciones.ESTADO_APROBADA,
                    fecha_inicio__year=anio_ciclo
                )
                
                empleados_list.append({
                    'empleado': emp,
                    'dias_disponibles': saldo.total_disponible(),
                    'dias_tomados': saldo.dias_consumidos_total(),
                    'vacaciones': list(vacaciones),
                })
            
            departamentos_data.append({
                'departamento': None,
                'empleados': empleados_list
            })

        context = {
            'anio_ciclo': anio_ciclo,
            'meses_data': meses_data,
            'departamentos_data': departamentos_data,
        }

        return render(request, 'gestion/calendario_global.html', context)
        
    except Exception as e:
        logger.error(f\"Error en calendario_global: {e}\")
        return render(request, 'gestion/error.html', {'error_message': str(e)})"""

content = content.replace(old_function, new_function)
print("Funcion calendario_global actualizada con semanas y departamentos")

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Archivo guardado!")
