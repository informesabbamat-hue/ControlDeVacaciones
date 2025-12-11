from datetime import date, timedelta

# Verificar el nuevo cálculo para 2025
primer_dia = date(2025, 1, 1)
print(f"1 de enero 2025: {primer_dia.strftime('%A')} (weekday={primer_dia.weekday()})")

dia_semana = primer_dia.weekday()
dias_hasta_domingo = (dia_semana + 1) % 7
fecha_inicio = primer_dia - timedelta(days=dias_hasta_domingo)

print(f"\nDía de semana: {dia_semana}")
print(f"Días hasta domingo: {dias_hasta_domingo}")
print(f"Fecha inicio: {fecha_inicio} ({fecha_inicio.strftime('%A')})")

# Primera semana
print("\nPrimera semana (Domingo a Sábado):")
for i in range(7):
    dia = fecha_inicio + timedelta(days=i)
    print(f"  {dia} ({dia.strftime('%A')})")
