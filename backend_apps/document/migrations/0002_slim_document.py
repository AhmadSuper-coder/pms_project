from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('document', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='gcs_bucket',
        ),
        migrations.RemoveField(
            model_name='document',
            name='checksum_md5',
        ),
        migrations.AlterField(
            model_name='document',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='patient.patient'),
        ),
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.CharField(max_length=100),
        ),
    ]


