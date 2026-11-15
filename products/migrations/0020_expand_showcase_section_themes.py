# Generated manually: expands ShowcaseSection.background_style choices from
# 3 themes to 9, per merchant request for more visual variety in the
# "Homepage Showcase Sections" theme picker. choices metadata only -- no
# column type change, so this is a safe no-op at the database level.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_alter_analyticsevent_options_alter_product_badge_tag_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showcasesection',
            name='background_style',
            field=models.CharField(
                max_length=20,
                default='light',
                choices=[
                    ('light', 'White / Minimal'),
                    ('cream', 'Soft Cream'),
                    ('brown', 'Warm Coffee Brown'),
                    ('dark', 'Charcoal Black'),
                    ('navy', 'Deep Navy'),
                    ('emerald', 'Emerald Green'),
                    ('rose', 'Rose Blush'),
                    ('slate', 'Cool Slate'),
                    ('gradient', 'Sunset Gradient'),
                ],
            ),
        ),
    ]






