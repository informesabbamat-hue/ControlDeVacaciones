from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.models import Empleado, Departamento
from datetime import date

class Command(BaseCommand):
    help = 'Crea un perfil de Empleado para el superusuario si no existe'

    def handle(self, *args, **options):
        # 1. Buscar superusuario
        try:
            superuser = User.objects.filter(is_superuser=True).first()
            if not superuser:
                self.stdout.write(self.style.ERROR('No se encontró ningún superusuario. Crea uno con "python manage.py createsuperuser"'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al buscar superusuario: {e}'))
            return

        # 2. Verificar si ya tiene perfil
        if hasattr(superuser, 'empleado'):
            self.stdout.write(self.style.SUCCESS(f'El superusuario "{superuser.username}" ya tiene un perfil de Empleado.'))
            return

        # 3. Crear Departamento por defecto si no existe
        depto, created = Departamento.objects.get_or_create(nombre='Administración')
        if created:
            self.stdout.write(self.style.SUCCESS('Departamento "Administración" creado.'))

        # 4. Crear Perfil de Empleado
        try:
            Empleado.objects.create(
                user=superuser,
                legajo='ADMIN',
                dni='00000000',
                nombre='Administrador',
                apellido='Sistema',
                departamento=depto,
                fecha_ingreso=date.today(),
                es_manager=True,
                jornada_estandar=8.0
            )
            self.stdout.write(self.style.SUCCESS(f'¡Perfil de Empleado creado exitosamente para "{superuser.username}"!'))
            self.stdout.write(self.style.SUCCESS('Ahora puedes iniciar sesión y ver el Dashboard.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al crear perfil de empleado: {e}'))
