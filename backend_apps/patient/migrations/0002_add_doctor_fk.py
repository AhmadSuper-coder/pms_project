from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('patient', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='doctor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='patients', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]


