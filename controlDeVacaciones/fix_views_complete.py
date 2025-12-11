import re

# Leer el archivo
with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar la sección rota de empleados_sin_depto
# La línea problemática es donde falta el cierre del bloque

# Encontrar la posición donde está el error
pattern = r'(saldo, created = SaldoVacaciones\.objects\.get_or_create\(\s+empleado=emp,\s+ciclo=anio_saldo,\s+defaults=\{\'dias_iniciales\': emp\.dias_base_lct\(anio_saldo\)\}\s+\))'

# Buscar la segunda ocurrencia (empleados sin departamento)
matches = list(re.finditer(pattern, content, re.MULTILINE))

if len(matches) >= 2:
    # Obtener la posición del segundo match
    second_match_end = matches[1].end()
    
    # Insertar el código faltante después del segundo get_or_create
    missing_code = '''
                
                # Días acumulados: usar dias_adicionales del saldo (cargados manualmente)
                dias_acumulados = saldo.dias_adicionales or 0
                
                # Días disponibles = total de días que tiene derecho (base + acumulados)
                # NO resta los consumidos - se muestra en columna "Disponible"
                dias_disponibles = saldo.dias_totales()
                
                # Días restantes = días disponibles - consumidos
                # Se muestra en columna "Restan"
                dias_restantes = saldo.total_disponible()
                
                vacaciones = RegistroVacaciones.objects.filter(
                    empleado=emp,
                    estado=RegistroVacaciones.ESTADO_APROBADA,
                    fecha_inicio__lte=fecha_fin_total,
                    fecha_fin__gte=fecha_inicio_total
                )
                
                empleados_list.append({
                    'empleado': emp,
                    'dias_disponibles': dias_disponibles,
                    'dias_acumulados': dias_acumulados,
                    'dias_restantes': dias_restantes,
                    'vacaciones': list(vacaciones),
                })
            '''
    
    # Insertar el código
    content = content[:second_match_end] + missing_code + content[second_match_end:]
    
    # Escribir el archivo
    with open('gestion/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: views.py fixed")
else:
    print(f"ERROR: Found {len(matches)} matches, expected at least 2")
