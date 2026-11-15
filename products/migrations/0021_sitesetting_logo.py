from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_expand_showcase_section_themes'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='site/'),
        ),
    ]
