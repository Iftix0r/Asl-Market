from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_debt'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Admin (botdan panel ochadi)'),
        ),
    ]
