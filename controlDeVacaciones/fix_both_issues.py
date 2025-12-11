"""
Script para corregir dos problemas en views.py:
1. Eliminar el filtro incorrecto en historial_global que solo muestra vacaciones activas
2. Actualizar calendario_global para manejar vacaciones que cruzan años
"""

# Leer el archivo
with open(r'c:\Sistemas ABBAMAT\ControlDeVacaciones\controlDeVacaciones\gestion\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# CORRECCIÓN 1: Eliminar el filtro de vacaciones activas en historial_global
old_historial = '''    # Asumiendo que RegistroVacaciones está disponible
    solicitudes_qs = RegistroVacaciones.objects.all()

    # 🔥 FILTRO NUEVO: solo vacaciones activas
    solicitudes_qs = solicitudes_qs.filter(
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    )

    if empleado_id and empleado_id != 'Todos':'''

new_historial = '''    # Asumiendo que RegistroVacaciones está disponible
    solicitudes_qs = RegistroVacaciones.objects.all()

    # Aplicar filtros opcionales
    if empleado_id and empleado_id != 'Todos':'''

content = content.replace(old_historial, new_historial)

# CORRECCIÓN 2: Actualizar calendario_global
old_calendario = '''@login_required
def calendario_global(request):
    """
    Vista que genera la tabla de planificación anual de vacaciones,
    agrupando las columnas por semanas (rangos de Lunes a Domingo).
    """
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
                rango_semanal = f"{fecha_inicio.day} al {fecha_fin.day}"

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
        print(f"ERROR: {e}")
        return render(request, 'gestion/error.html', {'error_message': str(e)})'''

new_calendario = '''@login_required
def calendario_global(request):
    """
    Vista que genera la tabla de planificación anual de vacaciones.
    Muestra empleados agrupados por departamento y semanas del año en columnas.
    """
    try:
        # 1. DEFINICIÓN DEL CICLO
        anio_ciclo = int(request.GET.get('anio', date.today().year))

        # 2. CALENDARIO ANUAL - Generar SEMANAS COMPLETAS del año (Domingo a Sábado)
        # Encontrar el domingo de la semana que contiene el 1 de enero
        primer_dia = date(anio_ciclo, 1, 1)
        dia_semana = primer_dia.weekday()  # 0=Lunes, 6=Domingo
        
        # Calcular días hasta el domingo anterior
        # Si es domingo (6), no retroceder. Si es lunes (0), retroceder 1 día, etc.
        dias_hasta_domingo = (dia_semana + 1) % 7
        
        # Retroceder hasta el domingo (puede ser del año anterior)
        fecha_inicio = primer_dia - timedelta(days=dias_hasta_domingo)
        
        # Generar todas las semanas del año
        todas_semanas = []
        fecha_actual = fecha_inicio
        
        # Continuar mientras la semana tenga al menos un día del año actual
        while True:
            # Crear semana de 7 días (Domingo a Sábado)
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
                
                # Obtener vacaciones aprobadas que se superponen con el año actual
                # CLAVE: Usamos fecha_inicio__lte y fecha_fin__gte para capturar vacaciones
                # que cruzan años (ej: 29/12/2025 al 4/1/2026)
                vacaciones = RegistroVacaciones.objects.filter(
                    empleado=emp,
                    estado=RegistroVacaciones.ESTADO_APROBADA,
                    fecha_inicio__lte=date(anio_ciclo, 12, 31),  # Comienza antes o durante el año
                    fecha_fin__gte=date(anio_ciclo, 1, 1)  # Termina durante o después del año
                )
                
                empleados_list.append({
                    'empleado': emp,
                    'dias_disponibles': saldo.total_disponible(),
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
                
                # Obtener vacaciones aprobadas que se superponen con el año actual
                vacaciones = RegistroVacaciones.objects.filter(
                    empleado=emp,
                    estado=RegistroVacaciones.ESTADO_APROBADA,
                    fecha_inicio__lte=date(anio_ciclo, 12, 31),  # Comienza antes o durante el año
                    fecha_fin__gte=date(anio_ciclo, 1, 1)  # Termina durante o después del año
                )
                
                empleados_list.append({
                    'empleado': emp,
                    'dias_disponibles': saldo.total_disponible(),
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
        logger.error(f"Error en calendario_global: {e}")
        return render(request, 'gestion/error.html', {'error_message': str(e)})'''

content = content.replace(old_calendario, new_calendario)

# Escribir el archivo
with open(r'c:\Sistemas ABBAMAT\ControlDeVacaciones\controlDeVacaciones\gestion\views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK - Correcciones aplicadas exitosamente:")
print("  1. Eliminado filtro de vacaciones activas en historial_global")
print("  2. Actualizado calendario_global para manejar vacaciones que cruzan años")
