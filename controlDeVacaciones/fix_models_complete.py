import re

# Leer el archivo
with open('gestion/models.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar la clase SaldoVacaciones y reescribir los métodos correctamente
output = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Buscar el inicio del método dias_consumidos_total que está roto
    if 'def dias_consumidos_total(self):' in line:
        # Escribir el método completo correctamente
        output.append('    def dias_consumidos_total(self):\n')
        output.append('        """Días de vacaciones consumidos en este ciclo."""\n')
        output.append('        consumido = RegistroVacaciones.objects.filter(\n')
        output.append('            empleado=self.empleado,\n')
        output.append('            fecha_inicio__year__gte=self.ciclo,\n')
        output.append("            estado='Aprobada'  # Solo contar solicitudes aprobadas\n")
        output.append("        ).aggregate(Sum('dias_solicitados'))['dias_solicitados__sum']\n")
        output.append('        \n')
        output.append('        return consumido or 0\n')
        output.append('\n')
        output.append('    def dias_totales(self):\n')
        output.append('        """\n')
        output.append('        Total de días que tiene derecho el empleado (base + acumulados).\n')
        output.append('        NO resta los días consumidos.\n')
        output.append('        Este valor se muestra en la columna "Disponible" del calendario.\n')
        output.append('        """\n')
        output.append('        dias_base_lct = self.empleado.dias_base_lct(self.ciclo)\n')
        output.append('        dias_acumulados = max(self.dias_iniciales, dias_base_lct)\n')
        output.append('        dias_adicionales = self.dias_adicionales or 0\n')
        output.append('        return dias_acumulados + dias_adicionales\n')
        output.append('\n')
        output.append('    def total_disponible(self):\n')
        output.append('        """\n')
        output.append('        Días restantes después de restar los consumidos.\n')
        output.append('        Este valor se muestra en la columna "Restan" del calendario.\n')
        output.append('        Fórmula: dias_totales() - dias_consumidos_total()\n')
        output.append('        """\n')
        output.append('        return self.dias_totales() - self.dias_consumidos_total()\n')
        output.append('\n')
        output.append('    @property\n')
        output.append('    def saldo_total(self):\n')
        output.append('        """\n')
        output.append('        Alias limpio para usar en el HTML.\n')
        output.append('        Es igual a total_disponible().\n')
        output.append('        """\n')
        output.append('        return self.total_disponible()\n')
        
        # Saltar las líneas rotas hasta encontrar __str__
        i += 1
        while i < len(lines) and 'def __str__(self):' not in lines[i]:
            i += 1
        continue
    
    output.append(line)
    i += 1

# Escribir el archivo corregido
with open('gestion/models.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print("SUCCESS: models.py fixed")
