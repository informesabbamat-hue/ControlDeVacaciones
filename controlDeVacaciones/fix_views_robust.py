# -*- coding: utf-8 -*-
import re

# Leer el archivo
with open('gestion/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar y eliminar la primera función duplicada (líneas 940-1013 aproximadamente)
in_first_duplicate = False
first_dup_start = -1
first_dup_end = -1

for i, line in enumerate(lines):
    # Buscar el inicio de la primera función duplicada
    if '@login_required' in line and i > 900 and i < 950:
        if i+2 < len(lines) and 'def aprobar_rechazar_solicitud' in lines[i+2]:
            first_dup_start = i
            in_first_duplicate = True
            continue
    
    # Buscar el final (el return redirect antes de la segunda función)
    if in_first_duplicate and "return redirect('gestion:historial_global')" in line:
        # Verificar que la siguiente función sea la segunda definición
        for j in range(i+1, min(i+10, len(lines))):
            if 'def aprobar_rechazar_solicitud' in lines[j]:
                first_dup_end = i + 1
                break
        if first_dup_end > 0:
            break

# Eliminar las líneas de la primera función duplicada
if first_dup_start > 0 and first_dup_end > 0:
    del lines[first_dup_start:first_dup_end]
    print(f"Eliminadas lineas {first_dup_start} a {first_dup_end}")

# Ahora buscar y reemplazar request.user por manager_empleado
# Primero encontrar donde insertar el código para obtener manager_empleado
for i, line in enumerate(lines):
    if 'def aprobar_rechazar_solicitud(request, solicitud_id):' in line:
        # Buscar la línea con accion = request.POST.get('accion')
        for j in range(i, min(i+20, len(lines))):
            if "accion = request.POST.get('accion')" in lines[j]:
                # Insertar el código después de esta línea y antes del try
                for k in range(j+1, min(j+10, len(lines))):
                    if 'try:' in lines[k]:
                        # Insertar aquí
                        indent = '    '
                        new_code = [
                            f"{indent}try:\n",
                            f"{indent}    # Obtener el Empleado asociado al usuario actual (manager)\n",
                            f"{indent}    try:\n",
                            f"{indent}        manager_empleado = Empleado.objects.get(user=request.user)\n",
                            f"{indent}    except Empleado.DoesNotExist:\n",
                            f'{indent}        messages.error(request, "Error: Tu usuario no esta asociado a un perfil de empleado.")\n',
                            f'{indent}        logger.error(f"Usuario {{request.user.username}} no tiene perfil de Empleado asociado")\n',
                            f"{indent}        return redirect('gestion:historial_global')\n",
                            f"{indent}    \n",
                        ]
                        # Reemplazar el try: original
                        lines[k] = ''.join(new_code)
                        print(f"Insertado codigo para obtener manager_empleado en linea {k}")
                        break
                break
        break

# Reemplazar request.user por manager_empleado en las asignaciones
for i, line in enumerate(lines):
    if 'solicitud.manager_aprobador = request.user' in line:
        lines[i] = line.replace('request.user', 'manager_empleado  # FIXED: Usar Empleado en lugar de User')
        print(f"Reemplazado request.user en linea {i}")

# Eliminar el filtro de fechas en historial_global
for i, line in enumerate(lines):
    if 'FILTRO NUEVO: solo vacaciones activas' in line:
        # Eliminar las siguientes 4 líneas del filtro
        for j in range(i, min(i+5, len(lines))):
            if 'fecha_fin__gte=hoy' in lines[j]:
                # Reemplazar todo el bloque
                lines[i] = '    # Mostrar todas las solicitudes (sin filtro de fechas para ver las pendientes)\n'
                # Eliminar las líneas del filtro
                del lines[i+1:j+2]
                print(f"Eliminado filtro de fechas en linea {i}")
                break
        break

# Guardar el archivo
with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\nArchivo corregido exitosamente!")
