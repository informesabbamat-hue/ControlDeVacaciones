# -*- coding: utf-8 -*-
# Script robusto para reemplazar la función calendario_global completa

with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar la función completa desde @login_required hasta el siguiente @login_required o def
import re

# Patrón para encontrar la función calendario_global completa
pattern = r'(@login_required\s+def calendario_global\(request\):.*?)((?=@login_required)|(?=@user_passes_test)|(?=def \w+\()|(?=class \w+))'

# Nueva función completa
nueva_funcion = '''@login_required
def calendario_global(request):
    """
    Vista que genera la tabla de planificación anual de vacaciones.
    Muestra empleados agrupados por departamento y semanas del año en columnas.
    """
    try:
        # 1. DEFINICIÓN DEL CICLO
        anio_ciclo = int(request.GET.get('anio', date.today().year))

        # 2. CALENDARIO ANUAL - Generar SEMANAS COMPLETAS del año (Lunes a Domingo)
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
        logger.error(f"Error en calendario_global: {e}")
        return render(request, 'gestion/error.html', {'error_message': str(e)})


'''

# Encontrar el inicio de la función
inicio = content.find('@login_required\ndef calendario_global(request):')
if inicio == -1:
    print("No se encontró la función calendario_global")
    exit(1)

# Encontrar el final (siguiente función o decorador)
# Buscar desde el inicio hacia adelante
resto = content[inicio + 50:]  # Saltar el inicio de la función actual
siguiente_def = resto.find('\n@login_required')
if siguiente_def == -1:
    siguiente_def = resto.find('\n@user_passes_test')
if siguiente_def == -1:
    siguiente_def = resto.find('\ndef ')

if siguiente_def == -1:
    print("No se encontró el final de la función")
    exit(1)

fin = inicio + 50 + siguiente_def

# Reemplazar
nuevo_content = content[:inicio] + nueva_funcion + content[fin:]

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(nuevo_content)

print("Función calendario_global reemplazada exitosamente!")
