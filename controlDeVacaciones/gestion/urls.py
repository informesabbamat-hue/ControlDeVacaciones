from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include

# Define el nombre de la aplicación (namespace) para poder usar 'gestion:nombre_ruta'
app_name = 'gestion' 

urlpatterns = [

    # --- Rutas de Uso General ---
    path('', views.dashboard, name='dashboard'),
    path('solicitud/', views.solicitar_vacaciones, name='solicitar_vacaciones'),
    path('calendario_global/', views.calendario_global, name='calendario_global'),
    path('calendario_global/exportar/', views.exportar_calendario_excel, name='exportar_calendario_excel'),
    
    # --- Rutas de Empleado (Personal) ---
    path('dias_disponibles/', views.dias_disponibles_view, name='dias_disponibles'), 
    # Usando 'historial_personal' como nombre para la vista
    path('mi_historial/', views.mi_historial, name='historial_personal'), 
    
    path('mi_perfil/', views.mi_perfil, name='mi_perfil'),
  

    # --- Rutas de Manager/Administración ---
    
    # 🌟 CRÍTICO: Ruta para la gestión de solicitudes por el manager
    path('aprobacion/manager/', views.aprobacion_manager, name='aprobacion_manager'),

    path('empleados/', views.gestion_empleados, name='gestion_empleados'),
    path('empleados/nuevo/', views.crear_empleado, name='crear_empleado'),
    path('empleados/<int:empleado_id>/editar/', views.editar_empleado, name='editar_empleado'),
    path('empleados/<int:empleado_id>/eliminar/', views.eliminar_empleado, name='eliminar_empleado'),
    path('historial_global/', views.historial_global, name='historial_global'),
    path('saldos/', views.gestion_saldos, name='gestion_saldos'),
    path('festivos/', views.gestion_festivos, name='gestion_festivos'),
    path('festivos/<int:festivo_id>/eliminar/', views.eliminar_festivo, name='eliminar_festivo'),
    path('calendario_manager/', views.calendario_manager, name='calendario_manager'),

    # --- Rutas de Utilidad (AJAX) ---
    path('saldo_ajax/', views.obtener_saldo_empleado, name='obtener_saldo_empleado'),
    path(
        'solicitud/<int:solicitud_id>/accion/', 
        views.aprobar_rechazar_solicitud, 
        name='aprobar_rechazar'
    ),
    
    # --- Exportación PDF ---
    path('notificacion-pdf/<int:empleado_id>/<int:vacacion_id>/', views.exportar_notificacion_vacaciones_pdf, name='exportar_notificacion_pdf'),
    


]