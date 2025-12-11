"""
Script para corregir la función aprobar_rechazar_solicitud
Elimina la primera versión duplicada y corrige la segunda
"""

# Leer el archivo
with open(r'c:\Sistemas ABBAMAT\ControlDeVacaciones\controlDeVacaciones\gestion\views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar y eliminar la primera función duplicada (líneas 1023-1096)
# Y corregir la segunda función

new_lines = []
skip_until_line = 0
in_first_function = False
in_second_function = False
line_num = 0

for i, line in enumerate(lines, 1):
    # Detectar el inicio de la primera función duplicada
    if i == 1023 and '@login_required' in line:
        in_first_function = True
        skip_until_line = 1097  # Saltar hasta después de la primera función
        continue
    
    # Saltar líneas de la primera función
    if in_first_function and i < skip_until_line:
        continue
    elif i == skip_until_line:
        in_first_function = False
        continue
    
    # Corregir la segunda función
    # Línea 1147: Eliminar saldo.dias_usados += dias_solicitados y saldo.save()
    if i >= 1146 and i <= 1148:
        if i == 1146:
            new_lines.append('                # NOTA: No es necesario descontar manualmente los dias porque el modelo\n')
            new_lines.append('                # SaldoVacaciones calcula automaticamente los dias consumidos a traves\n')
            new_lines.append('                # del metodo dias_consumidos_total() que cuenta las solicitudes aprobadas\n')
            new_lines.append('\n')
        continue
    
    # Línea 1152: Corregir manager_aprobador
    if i == 1152 and 'solicitud.manager_aprobador = request.user' in line:
        new_lines.append('                # Obtener el Empleado asociado al usuario actual (manager)\n')
        new_lines.append('                try:\n')
        new_lines.append('                    manager_empleado = Empleado.objects.get(user=request.user)\n')
        new_lines.append('                except Empleado.DoesNotExist:\n')
        new_lines.append('                    messages.error(request, "Error: Tu usuario no esta asociado a un perfil de empleado.")\n')
        new_lines.append('                    logger.error(f"Usuario {request.user.username} no tiene perfil de Empleado asociado")\n')
        new_lines.append('                    raise Exception("Manager sin perfil de empleado")\n')
        new_lines.append('\n')
        new_lines.append('                # Actualizar estado de la solicitud y guardar el objeto RegistroVacaciones\n')
        new_lines.append('                solicitud.estado = RegistroVacaciones.ESTADO_APROBADA\n')
        new_lines.append('                solicitud.manager_aprobador = manager_empleado\n')
        continue
    
    # Línea 1164: Corregir manager_aprobador en rechazar
    if i == 1164 and 'solicitud.manager_aprobador = request.user' in line:
        new_lines.append('                # Obtener el Empleado asociado al usuario actual (manager)\n')
        new_lines.append('                try:\n')
        new_lines.append('                    manager_empleado = Empleado.objects.get(user=request.user)\n')
        new_lines.append('                except Empleado.DoesNotExist:\n')
        new_lines.append('                    messages.error(request, "Error: Tu usuario no esta asociado a un perfil de empleado.")\n')
        new_lines.append('                    logger.error(f"Usuario {request.user.username} no tiene perfil de Empleado asociado")\n')
        new_lines.append('                    raise Exception("Manager sin perfil de empleado")\n')
        new_lines.append('\n')
        new_lines.append('                solicitud.estado = RegistroVacaciones.ESTADO_RECHAZADA\n')
        new_lines.append('                solicitud.manager_aprobador = manager_empleado\n')
        continue
    
    # Agregar la línea normalmente
    new_lines.append(line)

# Escribir el archivo
with open(r'c:\Sistemas ABBAMAT\ControlDeVacaciones\controlDeVacaciones\gestion\views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("OK - Funcion aprobar_rechazar_solicitud corregida:")
print("  1. Eliminada la primera version duplicada")
print("  2. Eliminado el campo inexistente dias_usados")
print("  3. Corregido manager_aprobador para usar objeto Empleado")
