
from datetime import date, timedelta
import calendar

def simulate_calendario(anio_ciclo):
    print(f"\n--- Simulating Calendar for {anio_ciclo} ---")
    
    primer_dia = date(anio_ciclo, 1, 1)
    dia_semana = primer_dia.weekday()  # 0=Lunes, 6=Domingo
    dias_hasta_domingo = (dia_semana + 1) % 7
    fecha_inicio = primer_dia - timedelta(days=dias_hasta_domingo)
    
    print(f"Primer día del año: {primer_dia} ({primer_dia.strftime('%A')})")
    print(f"Inicio de generación (Domingo anterior): {fecha_inicio}")
    
    todas_semanas = []
    fecha_actual = fecha_inicio
    
    while True:
        semana = []
        for i in range(7):
            semana.append(fecha_actual + timedelta(days=i))
        
        tiene_dias_del_ano = any(dia.year == anio_ciclo for dia in semana)
        
        if not tiene_dias_del_ano and semana[0].year > anio_ciclo:
            break
        
        if tiene_dias_del_ano:
            meses_en_semana = {}
            for dia in semana:
                if dia.year == anio_ciclo:
                    mes = dia.month
                    meses_en_semana[mes] = meses_en_semana.get(mes, 0) + 1
            
            if meses_en_semana:
                mes_principal = max(meses_en_semana, key=meses_en_semana.get)
                
                inicio = semana[0]
                fin = semana[6]
                rango = f"{inicio.day}/{inicio.month}-{fin.day}/{fin.month}"
                
                print(f"Week: {rango} | Assigned Month: {mes_principal} | Days in Year: {meses_en_semana}")
                
                todas_semanas.append({
                    'mes': mes_principal,
                    'rango': rango
                })
        
        fecha_actual += timedelta(days=7)

simulate_calendario(2025)
simulate_calendario(2026)
