# Generated by Django 4.1.4 on 2023-01-20 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course_app", "0014_alter_lecture_course_alter_lecture_home_work"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="paid_course",
        ),
        migrations.AddField(
            model_name="user",
            name="course_paid",
            field=models.ManyToManyField(blank=True, to="course_app.course"),
        ),
    ]