from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import JsonResponse 
# CORRECCIÓN 1: Asegurando que la importación de DiaFestivo sea correcta (singular)
from .models import Empleado, SaldoVacaciones, RegistroVacaciones, DiasFestivos, Departamento 
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from datetime import date, timedelta
from calendar import monthrange
import logging
# NUEVAS IMPORTACIONES REQUERIDAS para historial_global
from django.db.models import Sum, F 
from django import template
import sys 
import traceback
import calendar
import locale


logger = logging.getLogger(__name__)

# --- Clases y Funciones de Utilidad ---


# Definición de MESES_ESPANOL (Asegúrate de que esté definida en tu archivo)
MESES_ESPANOL = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}


try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        # Fallback para sistemas que usan otro nombre (ej. Windows)
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
    except locale.Error:
        # Fallback si no se puede configurar
        pass 



def generar_calendario_anual_intermensual(anio):
    """
    Genera la estructura del calendario anual (Ene a Dic) con semanas agrupadas
    de 7 días consecutivos, permitiendo que las semanas crucen meses.
    
    La estructura final agrupa las semanas por el mes en el que comienzan.
    """
    calendario_anual = {}
    
    # 1. Definir el rango del año: Desde el 1 de Enero hasta el 31 de Diciembre del año dado.
    fecha_inicio = date(anio, 1, 1)
    fecha_fin = date(anio, 12, 31) 
    
    # 2. Inicializar el puntero de fecha
    fecha_actual = fecha_inicio
    
    # Usamos un bucle while para avanzar de 7 en 7
    while fecha_actual <= fecha_fin:
        
        # 3. Crear una semana (7 días)
        dias_de_la_semana = []
        
        for i in range(7):
            dia_para_agregar = fecha_actual + timedelta(days=i)
            
            # Condición de salida: si ya hemos pasado demasiado el 31 de Diciembre.
            # (Lo mantenemos flexible para que la última semana de Diciembre se complete,
            # aunque los días caigan en el siguiente año).
            if dia_para_agregar > date(anio, 12, 31) + timedelta(days=6):
                break
                
            dias_de_la_semana.append(dia_para_agregar)

        # Si se agregaron días:
        if dias_de_la_semana:
            
            # Obtener el mes de inicio de esta semana para la cabecera.
            # Usamos %b (mes abreviado, ej: 'Jan', 'Dec') y lo pasamos a mayúsculas
            mes_inicio_semana = dias_de_la_semana[0].strftime('%b').upper()
            
            # Formato de los días: Solo el número de día
            dias_solo_numero = [d.day for d in dias_de_la_semana]

            semana_data = {
                'dias': dias_solo_numero,
                'num_columnas': len(dias_solo_numero),
                # Guardamos las fechas completas para el cálculo del rango en el filtro
                'fechas_completas': dias_de_la_semana, 
            }
            
            if mes_inicio_semana not in calendario_anual:
                calendario_anual[mes_inicio_semana] = []
            
            calendario_anual[mes_inicio_semana].append(semana_data)
        
        # 4. Avanzar a la siguiente semana (7 días)
        fecha_actual = fecha_actual + timedelta(days=7)
        
        # En caso de que se haya agregado una semana que empieza en Diciembre y termina en Enero del prox año,
        # detenemos el bucle después de procesarla.
        if fecha_actual.year > anio and fecha_actual.month == 1:
            break

    return calendario_anual


from django.shortcuts import render
from datetime import date, timedelta
from calendar import monthrange
# Asumimos que tienes modelos para Empleado
# from .models import Empleado 

def generar_calendario_anual(anio):
    """
    Genera una estructura de calendario anual, dividiendo el año en semanas completas (Lunes a Domingo).
    Si una semana cae en dos meses, se asigna al mes donde cae la mayoría de los días (o el inicio).
    
    Estructura de retorno:
    {
        'ENERO': [
            {'rango': '1/Ene al 5/Ene', 'dias': [date(2025, 1, 1), ...]},
            ...
        ],
        ...
    }
    """
    calendario_anual = {}
    
    # 1. Encontrar el primer día de planificación
    # Buscamos el Lunes más cercano al 1 de Enero del año.
    fecha_inicio = date(anio, 1, 1)
    # Lunes es 0 en Python. Restamos los días necesarios.
    # Ejemplo: Si el 1 de Enero es Miércoles (2), restamos 2 días para ir al Lunes (0).
    dias_para_lunes = fecha_inicio.weekday() 
    
    # Si el 1 de enero no es lunes (0), retrocedemos para empezar el primer lunes del ciclo.
    if dias_para_lunes != 0:
         fecha_inicio -= timedelta(days=dias_para_lunes)
         
    # 2. Iterar a lo largo del año en bloques de 7 días (semanas)
    fecha_actual = fecha_inicio
    
    # Iteramos hasta que pasemos el final del año (31 de Diciembre)
    while fecha_actual.year < anio + 1:
        
        dias_semana = []
        
        # Generar los 7 días (Lunes a Domingo)
        for i in range(7):
            dias_semana.append(fecha_actual + timedelta(days=i))
            
        # El rango de días para mostrar en el encabezado
        dia_inicio = dias_semana[0]
        dia_fin = dias_semana[-1]
        
        # El mes al que pertenece esta semana (usamos el mes del día de inicio)
        nombre_mes = dia_inicio.strftime('%B').upper()
        
        # Formato del rango de días
        rango_display = f"{dia_inicio.day} al {dia_fin.day}"
        
        # Si la semana cruza meses, incluimos el mes para mayor claridad (ej: 29/Dic al 4/Ene)
        if dia_inicio.month != dia_fin.month:
            rango_display = f"{dia_inicio.day}/{dia_inicio.month} al {dia_fin.day}/{dia_fin.month}"

        # 3. Almacenar en el calendario anual
        # Inicializar la lista si es la primera vez que vemos este mes
        if nombre_mes not in calendario_anual:
            calendario_anual[nombre_mes] = []
            
        # Añadir la semana a la lista. Usamos las claves: 'rango' y 'dias'
        calendario_anual[nombre_mes].append({
            'rango': rango_display, 
            'dias': dias_semana,
        })
        
        # Mover a la siguiente semana
        fecha_actual += timedelta(days=7)

    return calendario_anual

def calendario_global(request, anio=2025): # Asumo que esta es la vista que está dando error
    """
    Vista principal para mostrar la planificación de vacaciones.
    """
    
    calendario_anual = generar_calendario_anual(anio)
    
    # Datos de empleados de ejemplo para poblar la tabla
    empleados_planificacion = [
        {'apellido': 'Perez', 'nombre': 'Juan', 'f_ingreso': '20/05/2018', 'dias_disponibles': 21, 'dias_restantes': 15, 'planificacion': []},
        {'apellido': 'Gomez', 'nombre': 'Ana', 'f_ingreso': '10/11/2020', 'dias_disponibles': 14, 'dias_restantes': 10, 'planificacion': []},
    ]

    context = {
        'anio_ciclo': anio,
        'calendario_anual': calendario_anual,
        'empleados_planificacion': empleados_planificacion,
    }
    
    # !!! CORRECCIÓN CRÍTICA: La plantilla correcta es 'gestion/planificacion_calendario.html'
    # Asegúrate de que tu vista use este nombre de archivo, no 'gestion/error.html'.
    return render(request, 'gestion/planificacion_calendario.html', context)


class CustomLoginView(LoginView):
    def get_success_url(self):
        default_url = super().get_success_url()
        user = self.request.user

        if user.is_superuser:
            try:
                # CORRECCIÓN 2: El campo en Empleado es 'user', no 'usuario'
                Empleado.objects.get(user=user)
                return '/' 
            except Empleado.DoesNotExist:
                pass
        return default_url

# CORRECCIÓN ESTRUCTURAL: Se elimina la redefinición al final del archivo.
# Se usa esta versión robusta para el decorador @user_passes_test.
def is_manager(user):
    """Verifica si el usuario está autenticado y tiene un perfil de manager."""
    # Asegurarse de que el usuario tenga un perfil de empleado
    # NOTA: Si el error es de lógica de autorización, revisa qué lógica estás usando
    # (es_manager en el perfil vs. is_staff/grupos). Mantengo la versión robusta.
    return user.is_authenticated and hasattr(user, 'empleado') and user.empleado.es_manager

def calcular_dias_habiles(fecha_inicio, fecha_fin):
    """
    Calcula los días hábiles (laborables) entre dos fechas, 
    excluyendo sábados, domingos y días festivos registrados.
    """
    if fecha_inicio > fecha_fin:
        return 0
        
    delta = fecha_fin - fecha_inicio
    dias_habiles = 0
    
    # Obtener todos los días festivos en el rango para una consulta eficiente
    festivos = DiasFestivos.objects.filter(fecha__range=[fecha_inicio, fecha_fin]).values_list('fecha', flat=True)
    
    current_date = fecha_inicio
    while current_date <= fecha_fin:
        # 0 = Lunes, 6 = Domingo
        weekday = current_date.weekday()
        
        # 1. Excluir Sábados (5) y Domingos (6)
        if weekday < 5: 
            # 2. Excluir Días Festivos
            if current_date not in festivos:
                dias_habiles += 1
                
        current_date += timedelta(days=1)
        
    return dias_habiles

# --- Vistas Principales ---

@login_required
def dashboard(request):
    """Muestra el dashboard. Lógica simplificada para empleados no manager."""
    try:
        # CORRECCIÓN 3: Se usa 'user' para filtrar el Empleado
        empleado = Empleado.objects.get(user=request.user)
    except Empleado.DoesNotExist:
        if request.user.is_superuser:
            messages.error(request, "Tu cuenta de Superusuario no está vinculada a un registro de Empleado. Por favor, crea uno en el panel de Administración.")
            # Si es superusuario y no tiene perfil, lo redirige al admin
            return redirect('admin:index') 
        else:
            messages.error(request, "Error crítico: Usuario autenticado sin perfil de Empleado. Contacte a RR.HH.")
            # Si no es superusuario y no tiene perfil, lo redirige al login
            return redirect('/login/') 
            
    current_year = timezone.now().year
    context = {'empleado': empleado}
    
    # Esta parte se ejecuta para todos los empleados (managers o no managers)
    try:
        # Intenta obtener el saldo. Si no existe, se crea con LCT base por defecto
        saldo, created = SaldoVacaciones.objects.get_or_create(
            empleado=empleado, 
            ciclo=current_year,
            defaults={'dias_iniciales': empleado.dias_base_lct(current_year)}
        )
        context['saldo_disponible'] = saldo.total_disponible()
    except Exception:
        # En caso de error de DB o inicialización
        context['saldo_disponible'] = 0 
            
    return render(request, 'gestion/dashboard.html', context)


# --- VISTA para obtener saldo por AJAX ---
@login_required
@user_passes_test(is_manager)
def obtener_saldo_empleado(request):
    """Devuelve el saldo disponible de un empleado en formato JSON."""
    empleado_id = request.GET.get('empleado_id')
    current_year = timezone.now().year
    
    if not empleado_id:
        return JsonResponse({'error': 'Empleado ID no proporcionado'}, status=400)
    
    try:
        empleado_afectado = Empleado.objects.get(pk=empleado_id)
        
        # Obtener/Crear el SaldoVacaciones con LCT como valor inicial por defecto
        saldo, created = SaldoVacaciones.objects.get_or_create(
            empleado=empleado_afectado,
            ciclo=current_year,
            defaults={'dias_iniciales': empleado_afectado.dias_base_lct(current_year)}
        )
        
        saldo_disponible = saldo.total_disponible()
        
        return JsonResponse({
            'saldo_disponible': f"{saldo_disponible} días",
            'nombre_empleado': str(empleado_afectado),
            'estado': 'ok'
        })
        
    except Empleado.DoesNotExist:
        return JsonResponse({'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        logger.error(f"Error al obtener saldo por AJAX: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)



@login_required
@user_passes_test(is_manager) 
def solicitar_vacaciones(request):
    """
    Vista para que el Manager/RRHH registre días de ausencia para otro empleado.
    Las solicitudes se registran como 'Pendiente' para una posterior Aprobación/Rechazo.
    Utiliza DÍAS NATURALES para el cálculo y la validación.
    """
    current_year = timezone.now().year
    
    # Define el PERÍODO DE GOCE (Argentina: 1 de octubre al 30 de abril del año siguiente)
    start_goce = date(current_year, 10, 1)
    end_goce = date(current_year + 1, 4, 30)

    # Contexto base para GET y POST
    context = {
        'es_manager': True,
        'hoy': date.today().isoformat(),
        # Asumiendo que 'Empleado' es importado
        'todos_empleados': Empleado.objects.all().order_by('apellido', 'nombre'),
        # Usa POST como primera opción para mantener el valor en caso de error de POST
        'empleado_seleccionado_id': request.POST.get('empleado_id', request.GET.get('empleado_id')),
        'periodo_goce_inicio': start_goce.strftime("%d/%m/%Y"),
        'periodo_goce_fin': end_goce.strftime("%d/%m/%Y"),
        # Esto es lo que se muestra en pantalla:
        'estado_a_registrar': 'Pendiente', # CAMBIO 1: El estado visible ahora es Pendiente
    }
    context['saldo_disponible'] = 'N/A' 
    
    # LÓGICA DE CARGA INICIAL (para GET o errores de POST)
    empleado_id_inicial = context['empleado_seleccionado_id']
    if empleado_id_inicial:
        try:
            # Asumiendo que 'Empleado', 'SaldoVacaciones' y 'calcular_dias_lct' están importados
            empleado_afectado = Empleado.objects.get(pk=empleado_id_inicial)
            saldo, created = SaldoVacaciones.objects.get_or_create(
                empleado=empleado_afectado,
                ciclo=current_year,
                defaults={'dias_iniciales': empleado_afectado.dias_base_lct(current_year)}
            )
            
            context['saldo_disponible'] = f"{saldo.total_disponible()} días"
            
            if created:
                messages.warning(request, f"Advertencia: El saldo para {empleado_afectado.nombre} fue inicializado automáticamente con {saldo.dias_iniciales} días (LCT).")
            
        except Empleado.DoesNotExist:
            context['saldo_disponible'] = 'N/A' 
            messages.error(request, f"Error: No se encontró el empleado con ID {empleado_id_inicial}.")
        except Exception as e:
            messages.error(request, f"Error al calcular saldo para el empleado. Detalle: {e}")
            context['saldo_disponible'] = 'ERROR'
            
    # ----------------------------------------------------
    # PROCESAMIENTO DEL FORMULARIO POST
    # ----------------------------------------------------
    if request.method == 'POST':
        data = request.POST
        
        # 1. Identificar al Empleado Afectado
        empleado_id = data.get('empleado_id') 
        if not empleado_id:
            messages.error(request, "Debe seleccionar un empleado para completar la solicitud.")
            return render(request, 'gestion/solicitud.html', context)
            
        # Asumiendo que 'Empleado' está importado
        empleado_afectado = get_object_or_404(Empleado, pk=empleado_id)
            
        # 2. Obtener fechas y Validar formato
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_fin_str = data.get('fecha_fin')
        
        try:
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
            fecha_fin = date.fromisoformat(fecha_fin_str)
        except ValueError:
            messages.error(request, "Formato de fecha inválido. Por favor, use AAAA-MM-DD.")
            context['empleado_seleccionado_id'] = empleado_id
            return render(request, 'gestion/solicitud.html', context)
        
        if fecha_inicio > fecha_fin:
            messages.error(request, "La fecha de inicio no puede ser posterior a la fecha de fin.")
            context['empleado_seleccionado_id'] = empleado_id
            return render(request, 'gestion/solicitud.html', context)
        
        # 3. Validación de Período de Goce
        if fecha_inicio < start_goce or fecha_fin > end_goce:
            messages.error(request, f"Fechas fuera del período de goce permitido. Las vacaciones deben tomarse entre el {start_goce.strftime('%d/%m/%Y')} y el {end_goce.strftime('%d/%m/%Y')}.")
            context['empleado_seleccionado_id'] = empleado_id
            return render(request, 'gestion/solicitud.html', context)
        
        # 4. Re-cargar Saldo para el Empleado Afectado
        try:
            # Asumiendo que 'SaldoVacaciones' y 'calcular_dias_lct' están importados
            saldo, created = SaldoVacaciones.objects.get_or_create(
                empleado=empleado_afectado, 
                ciclo=current_year,
                defaults={'dias_iniciales': empleado_afectado.dias_base_lct(current_year)}
            )
            saldo_disponible = saldo.total_disponible()
        except Exception as e:
            messages.error(request, f"¡ERROR! No se pudo obtener el saldo para el empleado {empleado_afectado.nombre}. Detalle: {e}")
            context['empleado_seleccionado_id'] = empleado_id
            return render(request, 'gestion/solicitud.html', context)
            
        # 5. CORRECCIÓN CLAVE: Validaciones de Días Solicitados vs Saldo usando Días Naturales
        
        # 1. Calcular DÍAS NATURALES (Corridos) para la validación
        diferencia = fecha_fin - fecha_inicio
        dias_solicitados = diferencia.days + 1 # <--- Días Naturales
        
        if dias_solicitados <= 0:
            messages.warning(request, "El rango de fechas no es válido. La fecha de fin debe ser igual o posterior a la de inicio.")
            context['empleado_seleccionado_id'] = empleado_id
            return render(request, 'gestion/solicitud.html', context)

        if dias_solicitados > saldo_disponible:
            # Muestra los días naturales en el error
            messages.error(request, f"Saldo insuficiente. El empleado {empleado_afectado.nombre} solicita {dias_solicitados} días naturales, pero solo tiene {saldo_disponible} disponibles.")
            context['empleado_seleccionado_id'] = empleado_id
            return render(request, 'gestion/solicitud.html', context)

        # 6. Guardado Transaccional
        try:
            with transaction.atomic():
                # Asumiendo que 'RegistroVacaciones' está importado
                RegistroVacaciones.objects.create(
                    empleado=empleado_afectado, 
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    # Eliminamos 'dias_solicitados' ya que el método save() del modelo lo calcula
                    
                    # CAMBIO 2: Guardamos como 'Pendiente' en lugar de 'Aprobada'
                    estado='Pendiente', 
                    
                    # Eliminamos 'manager_aprobador' en la creación (se llena en la aprobación final)
                    manager_aprobador=None, 
                    
                    razon=data.get('razon') 
                )
                                
            # Mensaje de éxito modificado: indica que queda Pendiente
            messages.success(request, f"Solicitud de {dias_solicitados} días naturales para {empleado_afectado.nombre} registrada con éxito. Pendiente de aprobación.")
            
            # Redirigir a una vista de 'Aprobación Manager' (debes crearla)
            # return redirect('gestion:aprobacion_manager') 
            return redirect('gestion:historial_global') # Redirigimos al historial como fallback

        except Exception as e:
            messages.error(request, f"Error interno al procesar la solicitud. Detalle: {e}")
            context['empleado_seleccionado_id'] = empleado_id
            return render(request, 'gestion/solicitud.html', context)
    
    # RENDERIZADO (GET)
    return render(request, 'gestion/solicitud.html', context)


@login_required
@user_passes_test(is_manager)
def crear_empleado(request):
    departamentos = Departamento.objects.all().order_by('nombre')
    # Corregido: 'manager_aprobador' era antes 'reporta_a' en el código original, 
    # pero el modelo usa manager_aprobador
    managers_list = Empleado.objects.filter(es_manager=True).order_by('apellido')
    
    # Se usa 'user' en lugar de 'usuario_id' para la exclusión
    usuarios_con_perfil_existente = Empleado.objects.all().values_list('user__id', flat=True)
    usuarios_disponibles = User.objects.filter(is_active=True).exclude(id__in=usuarios_con_perfil_existente).order_by('username')
    
    contexto = {
        'titulo': 'Registrar Nuevo Empleado',
        'departamentos': departamentos,
        'managers_list': managers_list,
        'usuarios_disponibles': usuarios_disponibles,
    }

    if request.method == 'POST':
        data = request.POST
        errores = []
        if not data.get('usuario'):
            errores.append("Debe seleccionar un Usuario del Sistema.")
        # ... (otras validaciones) ...

        if errores:
            for error in errores:
                messages.error(request, error)
            contexto['post_data'] = data
            return render(request, 'gestion/crear_empleado.html', contexto)

        try:
            with transaction.atomic():
                user = User.objects.get(pk=data['usuario'])
                departamento_obj = Departamento.objects.get(pk=data['departamento'])
                
                manager_aprobador_obj = None
                # Asumo que el campo en el formulario se llama 'manager_aprobador' o similar
                if data.get('manager_aprobador'):
                    manager_aprobador_obj = Empleado.objects.get(pk=data['manager_aprobador'])

                empleado_nuevo = Empleado.objects.create(
                    # CORRECCIÓN 4: Se usa 'user' para el OneToOneField
                    user=user, 
                    legajo=data['legajo'],
                    dni=data['dni'],
                    nombre=data['nombre'],
                    apellido=data['apellido'],
                    departamento=departamento_obj,
                    fecha_ingreso=data['fecha_ingreso'],
                    es_manager=data.get('es_manager') == 'on',
                    manager_aprobador=manager_aprobador_obj # El modelo tiene manager_aprobador
                )
                
                # Se crea el Saldo con días_iniciales=0.00 para que el modelo lo calcule por LCT
                SaldoVacaciones.objects.get_or_create(
                    empleado=empleado_nuevo,
                    ciclo=timezone.now().year,
                    # Si no existe, se crea con el valor calculado por el modelo
                    defaults={'dias_iniciales': empleado_nuevo.dias_base_lct(timezone.now().year)}
                )
                
            messages.success(request, f"¡Empleado {data['nombre']} {data['apellido']} registrado con éxito! Saldo de vacaciones calculado automáticamente.")
            return redirect('gestion:gestion_empleados')
            
        except Exception as e:
            logger.error(f"Error interno al guardar el empleado: {e}")
            messages.error(request, f"Error interno al guardar el empleado. Detalle: {e}")
            contexto['post_data'] = data
            return render(request, 'gestion/crear_empleado.html', contexto)
    
    else:
        if not usuarios_disponibles.exists() and request.user.is_superuser:
            messages.warning(request, "No hay usuarios del sistema disponibles para asignar.")
            
        return render(request, 'gestion/crear_empleado.html', contexto)


@login_required
@user_passes_test(is_manager)
def calendario_manager(request):
    current_year = timezone.now().year
    start_date = date(current_year, 1, 1)
    # Ejemplo de rango, podría ser más dinámico
    end_date = date(current_year, 12, 31) 
    
    # Obtener empleados y agruparlos por departamento (usando consultas reales)
    empleados = Empleado.objects.all().select_related('departamento').order_by('departamento__nombre', 'apellido')
    empleados_por_departamento = {}
    
    for emp in empleados:
        depto_nombre = emp.departamento.nombre if emp.departamento else 'Sin Departamento'
        if depto_nombre not in empleados_por_departamento:
            empleados_por_departamento[depto_nombre] = []
        
        empleados_por_departamento[depto_nombre].append({
            'nombre': f"{emp.apellido}, {emp.nombre}", 
            'id': emp.pk
        })
    
    # Crear un rango de 150 días (por ejemplo) para la visualización del calendario
    rango_dias_visualizacion = 150 
    all_days_in_range = [start_date + timedelta(days=i) for i in range(rango_dias_visualizacion)] 
    
    context = {
        'empleados_por_departamento': empleados_por_departamento,
        'all_days_in_range': all_days_in_range,
        'current_year': current_year
    }
    return render(request, 'gestion/calendario.html', context)

@login_required
def mi_historial(request):
    # Obtener solicitudes y saldo del usuario actual
    try:
        empleado = Empleado.objects.get(user=request.user)
    except Empleado.DoesNotExist:
        messages.error(request, "Perfil de empleado no encontrado.")
        return redirect('dashboard') # Redirigir al dashboard para manejo de errores
    
    current_year = timezone.now().year
    
    # Se obtienen todas las solicitudes del empleado, ordenadas por fecha de inicio
    solicitudes = RegistroVacaciones.objects.filter(empleado=empleado).order_by('-fecha_inicio')
    
    # Se obtiene el saldo asegurando el cálculo LCT si no existe
    try:
        saldo, created = SaldoVacaciones.objects.get_or_create(
            empleado=empleado, 
            ciclo=current_year,
            defaults={'dias_iniciales': empleado.dias_base_lct(current_year)}
        )
        saldo_disponible = saldo.total_disponible()
    except Exception as e:
        logger.error(f"Error al calcular saldo para empleado {empleado.user.username}: {e}")
        messages.error(request, "Error al calcular días disponibles.")
        saldo_disponible = 'ERROR'
    
    
    context = {
        'empleado': empleado,
        'solicitudes': solicitudes,
        'saldo_disponible': saldo_disponible,
        'anio_ciclo': current_year
    }
    return render(request, 'gestion/mi_historial.html', context)

@login_required
def mi_perfil(request):
    # Permite al usuario actualizar datos de contacto/contraseña
    # En un proyecto real, se usaría un formulario de Django
    try:
        empleado = Empleado.objects.get(user=request.user)
    except Empleado.DoesNotExist:
        messages.error(request, "Perfil de empleado no encontrado.")
        return redirect('dashboard')

    context = {
        'empleado': empleado,
        'usuario': request.user # Acceso directo a datos del usuario
    }
    return render(request, 'gestion/mi_perfil.html', context)

@login_required
@user_passes_test(is_manager)
def historial_global(request):
    # --- 1. Lógica de Filtros ---
    hoy = datetime.now().date()
    
    empleado_id = request.GET.get('empleado')
    estado = request.GET.get('estado')

    # Asumiendo que RegistroVacaciones está disponible
    solicitudes_qs = RegistroVacaciones.objects.all()

    # 🔥 FILTRO NUEVO: solo vacaciones activas
    solicitudes_qs = solicitudes_qs.filter(
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    )

    if empleado_id and empleado_id != 'Todos':
        solicitudes_qs = solicitudes_qs.filter(empleado__id=empleado_id)

    if estado and estado != 'Todos':
        solicitudes_qs = solicitudes_qs.filter(estado=estado)
        
    solicitudes_qs = solicitudes_qs.order_by('-fecha_solicitud')
    
    # --- 2. Datos para Filtros y Resumen ---
    empleados_disponibles = Empleado.objects.order_by('apellido', 'nombre')
    
    # Cálculo del resumen (Días Aprobados)
    resumen_aprobado_data = RegistroVacaciones.objects.filter(
        estado=RegistroVacaciones.ESTADO_APROBADA, # Uso de la constante
        # Filtrar por solicitudes cuya fecha de inicio sea en el año actual
        fecha_inicio__year=datetime.now().year 
    ).values(
        'empleado__id', 
        'empleado__nombre', 
        'empleado__apellido',
        'empleado__legajo'  # <--- CAMBIO: Agregamos el campo legajo
    ).annotate(
        dias_aprobados=Sum('dias_solicitados')
    )
    
    context = {
        'solicitudes': solicitudes_qs,
        'empleados_disponibles': empleados_disponibles,
        # Necesitas definir esta tupla o lista en tu modelo RegistroVacaciones
        # EJEMPLO: ESTADOS = [('Pendiente', 'Pendiente'), ('Aprobada', 'Aprobada'), ...]
        'estados_disponibles': RegistroVacaciones.ESTADOS, 
        'empleado_id_seleccionado': empleado_id,
        'estado_seleccionado': estado,
        'resumen_aprobado': resumen_aprobado_data,
        'contexto': {'current_year': datetime.now().year},
    }
    
    # Renderizamos la plantilla
    return render(request, 'gestion/reportes.html', context)

@login_required
@user_passes_test(is_manager)
def gestion_empleados(request):
    try:
        # Aquí también es importante usar 'user' en el select_related si se necesita el User
        # Asumo que 'reporta_a' en el modelo Empleado es manager_aprobador
        empleados = Empleado.objects.all().select_related('departamento', 'manager_aprobador__user').order_by('apellido', 'nombre') 
    except Exception as e:
        messages.error(request, f"Error al cargar empleados: {e}")
        empleados = [] 

    contexto = {
        'empleados': empleados
    }
    return render(request, 'gestion/gestion_empleados.html', contexto)

@login_required
@user_passes_test(is_manager)
def gestion_saldos(request):
    # Obtener todos los saldos o datos para la gestión
    current_year = timezone.now().year
    saldos = SaldoVacaciones.objects.filter(ciclo=current_year).select_related('empleado__user', 'empleado__departamento').order_by('empleado__apellido')
    
    contexto = {
        'saldos': saldos,
        'anio_ciclo': current_year
    }
    return render(request, 'gestion/saldos.html', contexto)

@login_required
@user_passes_test(is_manager)
def gestion_festivos(request):
    # Corregido: La importación original era DiasFestivos (plural), pero la variable local era DiaFestivo (singular)
    # Usamos DiasFestivos, que es la importación correcta.
    festivos = DiasFestivos.objects.all().order_by('fecha') 
    contexto = {'festivos': festivos}
    return render(request, 'gestion/festivos.html', contexto)



@login_required
# @user_passes_test(is_manager, login_url='/gestion/no_autorizado/')
def dias_disponibles_view(request, empleado_id=None):
    print("--- INICIANDO dias_disponibles_view ---") 
    CICLO_ACTUAL = date.today().year

    empleado_a_ver = None
    saldo = None              
    saldo_total = 0.0
    dias_tomados = 0.0          
    dias_iniciales_saldo = 0.0  
    dias_adicionales = 0.0      
    dias_otorgados = 0.0        

    # 🔹 LISTADO DE EMPLEADOS PARA EL SELECT
    empleados = Empleado.objects.all().order_by("apellido", "nombre")
    empleado_id = request.GET.get("empleado_id")

    if empleado_id:
        empleado_a_ver = get_object_or_404(Empleado, id=empleado_id)
    else:
        try:
            empleado_a_ver = Empleado.objects.get(user=request.user)
        except Empleado.DoesNotExist:
            return render(request, 'gestion/error.html', {'mensaje': 'Usuario no asociado a un empleado.'})

    try:
        saldo = SaldoVacaciones.objects.get(
            empleado=empleado_a_ver, 
            ciclo=CICLO_ACTUAL
        )

        dias_iniciales_saldo = saldo.dias_iniciales or 0.0 
        dias_adicionales = saldo.dias_iniciales or 0.0
        dias_otorgados = dias_iniciales_saldo + dias_adicionales

        
        dias_tomados_agregado = RegistroVacaciones.objects.filter(
            empleado=empleado_a_ver,
            fecha_inicio__year=CICLO_ACTUAL,
            estado=RegistroVacaciones.ESTADO_APROBADA
        ).aggregate(
            total_tomados=Sum('dias_solicitados')
        )['total_tomados']
        

        dias_tomados = dias_tomados_agregado or 0.0
        
        saldo_total = dias_otorgados - dias_tomados
        
    except SaldoVacaciones.DoesNotExist:
        dias_tomados_agregado = RegistroVacaciones.objects.filter(
            empleado=empleado_a_ver,
            fecha_inicio__year=CICLO_ACTUAL, 
            estado=RegistroVacaciones.APROBADO 
        ).aggregate(
            total_tomados=Sum('dias_utilizados')
        )['total_tomados']
        
        dias_tomados = dias_tomados_agregado or 0.0
        saldo_total = dias_otorgados - dias_tomados 
        
    context = {
        'empleado': empleado_a_ver,
        'saldo': saldo,
        'ciclo_actual': CICLO_ACTUAL, 

        'dias_iniciales_saldo': dias_iniciales_saldo,
        'dias_adicionales': dias_adicionales,
        'dias_otorgados': dias_otorgados,
        'dias_tomados': dias_tomados,
        'saldo_total': saldo_total,

        # 🔹 LISTA DE EMPLEADOS PARA MOSTRAR EN EL SELECT
        'empleados': empleados,
    }

    return render(request, 'gestion/dias_disponibles.html', context)


def total_disponible(self):
    return self.dias_iniciales + self.dias_adicionales - self.dias_consumidos_total




@login_required
@user_passes_test(is_manager)
def aprobacion_manager(request):
    """Vista para que el Manager gestione las solicitudes pendientes de su equipo."""
    
    # Lógica real: Obtener solicitudes pendientes para este manager
    # solicitudes_pendientes = ... 
    
    context = {
        'solicitudes_pendientes': [] # Placeholder
    }
    return render(request, 'gestion/aprobacion_manager.html', context)


@login_required
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
        return render(request, 'gestion/error.html', {'error_message': str(e)})



@login_required
@user_passes_test(is_manager)
def aprobar_rechazar_solicitud(request, solicitud_id):
    """
    Procesa la aprobación o el rechazo de una solicitud de vacaciones
    y actualiza el saldo si se aprueba.
    """

    solicitud = get_object_or_404(RegistroVacaciones, pk=solicitud_id)
    empleado = solicitud.empleado
    dias_solicitados = solicitud.dias_solicitados  # Este campo ya está en el modelo

    if request.method != 'POST':
        messages.error(request, "Método no permitido.")
        return redirect('gestion:historial_global')

    accion = request.POST.get('accion')  # Puede ser 'aprobar' o 'rechazar'

    try:
        with transaction.atomic():
            # Validar que siga pendiente
            if solicitud.estado != RegistroVacaciones.ESTADO_PENDIENTE:
                messages.warning(request, f"La solicitud ya fue '{solicitud.estado}'.")
                return redirect('gestion:historial_global')

            # Obtener o crear saldo del empleado (usa campo ciclo, no ano)
            saldo, created = SaldoVacaciones.objects.get_or_create(
                empleado=empleado,
                ciclo=datetime.now().year,
                defaults={'dias_iniciales': empleado.dias_base_lct(datetime.now().year)}
            )

            # ✅ Acción de aprobar
            if accion == 'aprobar':
                if saldo.total_disponible() < dias_solicitados:
                    messages.error(
                        request,
                        f"Saldo insuficiente. {empleado.nombre} tiene {saldo.total_disponible()} días y solicita {dias_solicitados}."
                    )
                    raise Exception("Saldo insuficiente.")

                # Descontar saldo
                saldo.dias_usados += dias_solicitados
                saldo.save()

                solicitud.estado = RegistroVacaciones.ESTADO_APROBADA
                solicitud.manager_aprobador = request.user
                solicitud.fecha_aprobacion = date.today()
                solicitud.save()

                messages.success(
                    request,
                    f"Vacaciones de {empleado.nombre} APROBADAS. "
                    f"Se descontaron {dias_solicitados} días. Nuevo saldo: {saldo.total_disponible()} días."
                )

            # 🚫 Acción de rechazar
            elif accion == 'rechazar':
                solicitud.estado = RegistroVacaciones.ESTADO_RECHAZADA
                solicitud.manager_aprobador = request.user
                solicitud.fecha_aprobacion = date.today()
                solicitud.save()

                messages.warning(request, f"Vacaciones de {empleado.nombre} RECHAZADAS. El saldo no fue afectado.")

            else:
                messages.error(request, "Acción inválida.")
                raise Exception("Acción inválida.")

    except Exception as e:
        logger.error(f"Error al aprobar/rechazar solicitud: {e}")
        messages.error(request, f"Error al procesar la acción: {e}")

    return redirect('gestion:historial_global')


@login_required
# Asume que 'is_manager' está definido y verifica la jerarquía.
@user_passes_test(is_manager)
def aprobar_rechazar_solicitud(request, solicitud_id):
    """
    Procesa la aprobación o el rechazo de una solicitud de vacaciones
    para un empleado y actualiza el saldo si se aprueba.
    """

    # Obtener la solicitud o devolver 404 si no existe
    solicitud = get_object_or_404(RegistroVacaciones, pk=solicitud_id)
    empleado = solicitud.empleado
    dias_solicitados = solicitud.dias_solicitados

    # Solo permitir la acción via POST
    if request.method != 'POST':
        messages.error(request, "Método no permitido. Utiliza el formulario.")
        return redirect('gestion:historial_global')

    accion = request.POST.get('accion')  # Debe ser 'aprobar' o 'rechazar'

    try:
        # Usar transacciones atómicas para asegurar que el saldo y la solicitud se actualicen juntos
        with transaction.atomic():
            # 1. Validar estado actual de la solicitud
            if solicitud.estado != RegistroVacaciones.ESTADO_PENDIENTE:
                messages.warning(request, f"La solicitud ya fue procesada y está en estado: '{solicitud.estado}'.")
                return redirect('gestion:historial_global')

            # 2. Obtener o crear el saldo de vacaciones para el ciclo (año) actual
            ciclo_actual = datetime.now().year
            saldo, created = SaldoVacaciones.objects.get_or_create(
                empleado=empleado,
                ciclo=ciclo_actual,
                defaults={'dias_iniciales': empleado.dias_base_lct(ciclo_actual)}
            )

            if accion == 'aprobar':
                # 3. ✅ Acción de aprobar: Validar saldo y descontar
                if saldo.total_disponible() < dias_solicitados:
                    # Si el saldo es insuficiente, se lanza una excepción que aborta la transacción
                    messages.error(
                        request,
                        f"Saldo insuficiente. {empleado.nombre} tiene {saldo.total_disponible()} días disponibles y solicita {dias_solicitados}."
                    )
                    raise Exception("Fallo en la aprobación: Saldo insuficiente.")

                # Descontar saldo y guardar el objeto SaldoVacaciones
                saldo.dias_usados += dias_solicitados
                saldo.save()

                # Actualizar estado de la solicitud y guardar el objeto RegistroVacaciones
                solicitud.estado = RegistroVacaciones.ESTADO_APROBADA
                solicitud.manager_aprobador = request.user
                solicitud.fecha_aprobacion = date.today()
                solicitud.save()

                messages.success(
                    request,
                    f"Vacaciones de {empleado.nombre} APROBADAS. Se descontaron {dias_solicitados} días. Nuevo saldo: {saldo.total_disponible()} días."
                )

            elif accion == 'rechazar':
                # 4. 🚫 Acción de rechazar: Actualizar estado sin modificar saldo
                solicitud.estado = RegistroVacaciones.ESTADO_RECHAZADA
                solicitud.manager_aprobador = request.user
                solicitud.fecha_aprobacion = date.today()
                solicitud.save()

                messages.warning(request, f"Vacaciones de {empleado.nombre} RECHAZADAS. El saldo no fue afectado.")

            else:
                # 5. Acción inválida
                messages.error(request, f"Acción '{accion}' inválida o no reconocida.")
                raise Exception("Acción de formulario no válida ('aprobar' o 'rechazar').")

    except Exception as e:
        logger.error(f"Error procesando solicitud {solicitud_id}: {e}")
        # Si la excepción no fue por saldo insuficiente, mostrar un mensaje de error más general
        if not str(e).startswith("Fallo en la aprobación: Saldo insuficiente."):
             messages.error(request, "Error interno al procesar la solicitud. Contacta a soporte.")
        # La transacción.atomic() maneja el rollback automáticamente aquí.

    return redirect('gestion:historial_global')