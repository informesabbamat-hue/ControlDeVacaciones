from django.contrib import admin
from .models import (
    Empleado, 
    SaldoVacaciones, 
    DiasFestivos, 
    RegistroVacaciones, 
    Departamento
)


# Personalización opcional del panel de administración para Empleado
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'legajo', 'departamento', 'fecha_ingreso', 'es_manager')
    search_fields = ('legajo', 'nombre', 'apellido', 'dni')
    list_filter = ('departamento', 'es_manager')
    

# Personalización opcional del panel de administración para RegistroVacaciones
class RegistroVacacionesAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'estado', 'fecha_solicitud')
    list_filter = ('estado', 'fecha_solicitud', 'empleado__departamento')
    search_fields = ('empleado__legajo', 'empleado__nombre', 'empleado__apellido')


# Personalización opcional del panel de administración para SaldoVacaciones
class SaldoVacacionesAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'ciclo', 'dias_iniciales', 'dias_adicionales', 'total_disponible')
    list_filter = ('ciclo', 'empleado__departamento')
    search_fields = ('empleado__legajo', 'empleado__apellido')
    list_editable = ('dias_adicionales',)  # Permite editar días adicionales directamente desde la lista

# Registro de los modelos en el sitio de administración
admin.site.register(Departamento)
admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(SaldoVacaciones, SaldoVacacionesAdmin)
admin.site.register(DiasFestivos)
admin.site.register(RegistroVacaciones, RegistroVacacionesAdmin)