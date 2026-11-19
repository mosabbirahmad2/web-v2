from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_alter_sitesetting_announcement_notice'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=120)),
                ('image', models.ImageField(upload_to='hero_banners/')),
                ('link', models.CharField(blank=True, default='', max_length=255)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='brand_font',
            field=models.CharField(
                choices=[
                    ('Plus Jakarta Sans', 'Plus Jakarta Sans (Modern Clean)'),
                    ('Montserrat', 'Montserrat (Bold Geometric)'),
                    ('Poppins', 'Poppins (Friendly Modern)'),
                    ('Playfair Display', 'Playfair Display (Luxury Serif)'),
                    ('Cinzel', 'Cinzel (Royal Boutique)'),
                    ('Cormorant Garamond', 'Cormorant Garamond (Editorial)'),
                    ('Space Grotesk', 'Space Grotesk (Tech Contemporary)'),
                    ('Syne', 'Syne (Avant-Garde Brand)'),
                    ('Oswald', 'Oswald (Strong Condensed)'),
                    ('Bebas Neue', 'Bebas Neue (Impact Display)'),
                ],
                default='Plus Jakarta Sans',
                max_length=60,
            ),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='enable_free_delivery',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='show_brand_name_with_logo',
            field=models.BooleanField(default=True),
        ),
    ]
