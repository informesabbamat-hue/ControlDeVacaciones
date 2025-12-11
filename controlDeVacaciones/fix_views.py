# Script to fix the corrupted views.py file
import re

# Read the corrupted file
with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where calendario_global function starts
calendario_start = content.find('def calendario_global(request):')

# Find where the corruption starts (the incomplete context = {)
corruption_start = content.find('        context = {\n@user_passes_test(is_manager)')

if corruption_start == -1:
    corruption_start = content.find('        context = {\n    # Obtener la solicitud')

# Find where aprobar_rechazar_solicitud should properly start  
proper_function_start = content.find('@login_required\n@user_passes_test(is_manager)\ndef aprobar_rechazar_solicitud(request, solicitud_id):')

if proper_function_start == -1:
    proper_function_start = content.find('def aprobar_rechazar_solicitud(request, solicitud_id):')

# Find the end of aprobar_rechazar_solicitud
function_end = content.find("    return redirect('gestion:historial_global')", proper_function_start)
if function_end != -1:
    function_end = content.find('\n', function_end) + 1

print(f"calendario_start: {calendario_start}")
print(f"corruption_start: {corruption_start}")
print(f"proper_function_start: {proper_function_start}")
print(f"function_end: {function_end}")

# Extract the good part of aprobar_rechazar_solicitud
if proper_function_start != -1 and function_end != -1:
    good_function = content[proper_function_start:function_end]
    print("\n=== GOOD FUNCTION EXTRACTED ===")
    print(good_function[:500])
