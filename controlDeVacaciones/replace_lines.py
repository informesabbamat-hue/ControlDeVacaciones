
import os

file_path = r'c:\Sistemas ABBAMAT\ControlDeVacaciones\controlDeVacaciones\gestion\views.py'

new_code = """@login_required
@user_passes_test(is_manager)
def aprobar_rechazar_solicitud(request, solicitud_id):
    \"\"\"
    Procesa la aprobación o el rechazo de una solicitud de vacaciones
    para un empleado y actualiza el saldo si se aprueba.
    \"\"\"

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
        # Obtener el Empleado asociado al usuario actual (manager)
        try:
            manager_empleado = Empleado.objects.get(user=request.user)
        except Empleado.DoesNotExist:
            messages.error(request, "Error: Tu usuario no está asociado a un perfil de empleado.")
            logger.error(f"Usuario {request.user.username} no tiene perfil de Empleado asociado")
            return redirect('gestion:historial_global')

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
                # 3. Acción de aprobar: Validar saldo
                if saldo.total_disponible() < dias_solicitados:
                    messages.error(
                        request,
                        f"Saldo insuficiente. {empleado.nombre} tiene {saldo.total_disponible()} días disponibles y solicita {dias_solicitados}."
                    )
                    raise Exception("Fallo en la aprobación: Saldo insuficiente.")

                # NOTA: No es necesario descontar manualmente los días porque el modelo
                # SaldoVacaciones calcula automáticamente los días consumidos.
                
                # Actualizar estado de la solicitud y guardar el objeto RegistroVacaciones
                solicitud.estado = RegistroVacaciones.ESTADO_APROBADA
                solicitud.manager_aprobador = manager_empleado
                solicitud.fecha_aprobacion = date.today()
                solicitud.save()

                messages.success(
                    request,
                    f"Vacaciones de {empleado.nombre} APROBADAS. Se descontaron {dias_solicitados} días. Nuevo saldo: {saldo.total_disponible()} días."
                )

            elif accion == 'rechazar':
                # 4. Acción de rechazar: Actualizar estado sin modificar saldo
                solicitud.estado = RegistroVacaciones.ESTADO_RECHAZADA
                solicitud.manager_aprobador = manager_empleado
                solicitud.fecha_aprobacion = date.today()
                solicitud.save()

                messages.warning(request, f"Vacaciones de {empleado.nombre} RECHAZADAS. El saldo no fue afectado.")

            else:
                # 5. Acción inválida
                messages.error(request, f"Acción '{accion}' inválida o no reconocida.")
                raise Exception("Acción de formulario no válida ('aprobar' o 'rechazar').")

    except Exception as e:
        logger.error(f"Error procesando solicitud {solicitud_id}: {e}")
        if not str(e).startswith("Fallo en la aprobación: Saldo insuficiente."):
             messages.error(request, "Error interno al procesar la solicitud. Contacta a soporte.")

    return redirect('gestion:historial_global')
"""

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replace lines 1023-1182 (indices 1022-1182)
# Note: Python list slicing is [start:end], so we need index 1022 to 1182
# Line 1023 is index 1022.
# Line 1182 is index 1181.
# So we want to replace lines[1022:1182]

start_line = 1023
end_line = 1182

# Validate that we are replacing the right thing
if "@login_required" not in lines[start_line-1]:
    print(f"Error: Line {start_line} does not start with @login_required. It is: {lines[start_line-1]}")
    exit(1)

# Construct the new file content
final_lines = lines[:start_line-1] + [new_code + '\n'] + lines[end_line:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print("Successfully replaced lines 1023-1182 with corrected code.")
