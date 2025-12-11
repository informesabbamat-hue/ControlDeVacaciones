# -*- coding: utf-8 -*-
# Script final para corregir views.py

with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Eliminar la primera función duplicada
lines = content.split('\n')
new_lines = []
skip_until = -1

for i, line in enumerate(lines):
    if skip_until > 0 and i < skip_until:
        continue
    
    # Detectar inicio de la primera función duplicada
    if i > 900 and i < 950 and '@login_required' in line:
        if i+2 < len(lines) and 'def aprobar_rechazar_solicitud' in lines[i+2]:
            # Buscar el final
            for j in range(i, min(i+100, len(lines))):
                if "return redirect('gestion:historial_global')" in lines[j]:
                    # Verificar que hay otra definición después
                    for k in range(j+1, min(j+10, len(lines))):
                        if 'def aprobar_rechazar_solicitud' in lines[k]:
                            skip_until = j + 1
                            print(f"Eliminando lineas {i} a {j}")
                            break
                    if skip_until > 0:
                        break
    
    if skip_until < 0 or i >= skip_until:
        new_lines.append(line)

content = '\n'.join(new_lines)

# 2. Agregar obtención de manager_empleado
old = """    accion = request.POST.get('accion')  # Debe ser 'aprobar' o 'rechazar'

    try:
        # Usar transacciones atómicas"""

new = """    accion = request.POST.get('accion')  # Debe ser 'aprobar' o 'rechazar'

    try:
        # Obtener el Empleado asociado al usuario actual (manager)
        try:
            manager_empleado = Empleado.objects.get(user=request.user)
        except Empleado.DoesNotExist:
            messages.error(request, "Error: Tu usuario no esta asociado a un perfil de empleado.")
            logger.error(f"Usuario {request.user.username} no tiene perfil de Empleado asociado")
            return redirect('gestion:historial_global')
        
        # Usar transacciones atómicas"""

content = content.replace(old, new)
print("Agregada obtencion de manager_empleado")

# 3. Eliminar las líneas de dias_usados
old_block = """                # Descontar saldo y guardar el objeto SaldoVacaciones
                saldo.dias_usados += dias_solicitados
                saldo.save()

                # Actualizar estado de la solicitud y guardar el objeto RegistroVacaciones"""

new_block = """                # Actualizar estado de la solicitud y guardar el objeto RegistroVacaciones
                # NOTA: No es necesario descontar manualmente los días porque el modelo
                # SaldoVacaciones calcula automáticamente los días consumidos a través
                # del método dias_consumidos_total() que cuenta las solicitudes aprobadas"""

content = content.replace(old_block, new_block)
print("Eliminadas lineas de dias_usados")

# 4. Reemplazar request.user por manager_empleado
content = content.replace(
    "solicitud.manager_aprobador = request.user",
    "solicitud.manager_aprobador = manager_empleado  # FIXED"
)
print("Reemplazado request.user por manager_empleado")

# 5. Eliminar filtro de fechas
old_filter = """    # 🔥 FILTRO NUEVO: solo vacaciones activas
    solicitudes_qs = solicitudes_qs.filter(
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    )"""

new_filter = "    # Mostrar todas las solicitudes (sin filtro de fechas para ver las pendientes)"

content = content.replace(old_filter, new_filter)
print("Eliminado filtro de fechas")

# Guardar
with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nArchivo corregido!")
