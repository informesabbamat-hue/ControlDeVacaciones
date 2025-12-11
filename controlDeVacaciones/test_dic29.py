from datetime import date, timedelta

# Verificar qué día es el 29 de diciembre 2024
dic_29 = date(2024, 12, 29)
print(f"29 de diciembre 2024: {dic_29.strftime('%A')} (weekday={dic_29.weekday()})")

dic_30 = date(2024, 12, 30)
print(f"30 de diciembre 2024: {dic_30.strftime('%A')} (weekday={dic_30.weekday()})")

# Si la primera semana debe ser 29/12 al 4/1, entonces:
print("\nSi la semana empieza el 29:")
semana_desde_29 = []
for i in range(7):
    dia = dic_29 + timedelta(days=i)
    semana_desde_29.append(dia)
    print(f"  {dia} ({dia.strftime('%A')})")
