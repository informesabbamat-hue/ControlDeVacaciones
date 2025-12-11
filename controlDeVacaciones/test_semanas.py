from datetime import date, timedelta

# Verificar para 2025
primer_dia = date(2025, 1, 1)
print(f"1 de enero 2025: {primer_dia.strftime('%A')} (weekday={primer_dia.weekday()})")

dias_hasta_lunes = primer_dia.weekday()
fecha_inicio = primer_dia - timedelta(days=dias_hasta_lunes)
print(f"Fecha inicio calculada: {fecha_inicio} ({fecha_inicio.strftime('%A')})")
print(f"Dias retrocedidos: {dias_hasta_lunes}")

# La primera semana debería ser
semana1 = []
for i in range(7):
    semana1.append(fecha_inicio + timedelta(days=i))

print("\nPrimera semana:")
for dia in semana1:
    print(f"  {dia} ({dia.strftime('%A')})")
