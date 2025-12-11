# Script para arreglar views.py
with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Eliminar la función duplicada (líneas 940-1013)
# Buscar el inicio de la primera función duplicada
first_duplicate_start = content.find('\n@login_required\n@user_passes_test(is_manager)\ndef aprobar_rechazar_solicitud(request, solicitud_id):\n    """\n    Procesa la aprobación o el rechazo de una solicitud de vacaciones\n    y actualiza el saldo si se aprueba.\n    """')

if first_duplicate_start != -1:
    # Buscar el final de esta función (el return redirect antes de la segunda definición)
    first_duplicate_end = content.find('\n    return redirect(\'gestion:historial_global\')\n\n\n@login_required\n# Asume que \'is_manager\'', first_duplicate_start)
    
    if first_duplicate_end != -1:
        # Eliminar la primera función duplicada
        content = content[:first_duplicate_start] + content[first_duplicate_end + len('\n    return redirect(\'gestion:historial_global\')'):]
        print("✓ Función duplicada eliminada")

# 2. Reemplazar request.user por manager_empleado
# Primero agregar la obtención del manager_empleado
old_code = """    accion = request.POST.get('accion')  # Debe ser 'aprobar' o 'rechazar'

    try:
        # Usar transacciones atómicas"""

new_code = """    accion = request.POST.get('accion')  # Debe ser 'aprobar' o 'rechazar'

    try:
        # Obtener el Empleado asociado al usuario actual (manager)
        try:
            manager_empleado = Empleado.objects.get(user=request.user)
        except Empleado.DoesNotExist:
            messages.error(request, "Error: Tu usuario no está asociado a un perfil de empleado.")
            logger.error(f"Usuario {request.user.username} no tiene perfil de Empleado asociado")
            return redirect('gestion:historial_global')
        
        # Usar transacciones atómicas"""

content = content.replace(old_code, new_code)
print("✓ Agregada obtención de manager_empleado")

# 3. Reemplazar las asignaciones de request.user por manager_empleado
content = content.replace(
    "                solicitud.manager_aprobador = request.user",
    "                solicitud.manager_aprobador = manager_empleado  # FIXED: Usar Empleado en lugar de User"
)
print("✓ Reemplazadas asignaciones de manager_aprobador")

# 4. Eliminar el filtro de fechas en historial_global
old_filter = """    # 🔥 FILTRO NUEVO: solo vacaciones activas
    solicitudes_qs = solicitudes_qs.filter(
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    )"""

new_filter = "    # Mostrar todas las solicitudes (sin filtro de fechas para ver las pendientes)"

content = content.replace(old_filter, new_filter)
print("✓ Filtro de fechas eliminado en historial_global")

# Guardar el archivo corregido
with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Archivo views.py corregido exitosamente!")
