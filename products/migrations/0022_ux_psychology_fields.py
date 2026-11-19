from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0021_sitesetting_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='free_delivery_threshold',
            field=models.DecimalField(decimal_places=2, default=600.0, max_digits=8),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='hero_badge',
            field=models.CharField(blank=True, default='New Drop 2026', max_length=80),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='hero_image',
            field=models.ImageField(blank=True, null=True, upload_to='site/'),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='hero_subtitle',
            field=models.TextField(blank=True, default='Carefully crafted cases and everyday key rings at honest prices — inspect on delivery and pay only when you love it.'),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='hero_title',
            field=models.CharField(blank=True, default='Phone Covers & Key Rings Designed to Stand Out', max_length=160),
        ),
    ]
