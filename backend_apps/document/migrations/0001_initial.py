from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patient', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('content_type', models.CharField(max_length=150)),
                ('gcs_bucket', models.CharField(max_length=255)),
                ('gcs_key', models.CharField(max_length=512, unique=True)),
                ('size_bytes', models.BigIntegerField(blank=True, null=True)),
                ('checksum_md5', models.CharField(blank=True, max_length=64, null=True)),
                ('document_type', models.CharField(blank=True, max_length=100, null=True)),
                ('is_uploaded', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documents', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='patient.patient')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]


