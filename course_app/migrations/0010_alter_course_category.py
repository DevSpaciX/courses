# Generated by Django 4.1.5 on 2023-01-19 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("course_app", "0009_user_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="course",
                to="course_app.category",
            ),
        ),
    ]
