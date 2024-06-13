# Generated by Django 5.0.6 on 2024-06-13 13:25

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sessions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CharacterClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Chest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('item_type', models.CharField(choices=[('Weapon', 'Weapon'), ('Potion', 'Potion'), ('Manuscript', 'Manuscript'), ('Gold', 'Gold'), ('Silver', 'Silver'), ('Food', 'Food'), ('Equipment', 'Equipment')], max_length=255)),
                ('is_equipped', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
                ('stats', models.JSONField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('power', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='World',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('hp', models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)])),
                ('session_key', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sessions.session')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('character_class', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.characterclass')),
            ],
        ),
        migrations.CreateModel(
            name='ChestItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.chest')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.item')),
            ],
        ),
        migrations.AddField(
            model_name='chest',
            name='inventory',
            field=models.ManyToManyField(through='api.ChestItem', to='api.item'),
        ),
        migrations.CreateModel(
            name='CharacterInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.character')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.item')),
            ],
        ),
        migrations.AddField(
            model_name='character',
            name='inventory',
            field=models.ManyToManyField(through='api.CharacterInventory', to='api.item'),
        ),
        migrations.CreateModel(
            name='ShopItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(default=0)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.item')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.shop')),
            ],
        ),
        migrations.AddField(
            model_name='shop',
            name='inventory',
            field=models.ManyToManyField(through='api.ShopItem', to='api.item'),
        ),
        migrations.CreateModel(
            name='CharacterSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.character')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.skill')),
            ],
        ),
        migrations.AddField(
            model_name='character',
            name='skills',
            field=models.ManyToManyField(through='api.CharacterSkill', to='api.skill'),
        ),
        migrations.CreateModel(
            name='Tile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posX', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('posY', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('visited', models.BooleanField(default=False)),
                ('east_door', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='east_connected_tile', to='api.tile')),
                ('north_door', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='north_connected_tile', to='api.tile')),
                ('south_door', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='south_connected_tile', to='api.tile')),
                ('west_door', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='west_connected_tile', to='api.tile')),
                ('link_world', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.world')),
                ('portal_to_world', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portal_tiles', to='api.world')),
            ],
        ),
        migrations.AddField(
            model_name='shop',
            name='tile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile'),
        ),
        migrations.CreateModel(
            name='SavedGameState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inventory_data', models.TextField(blank=True)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.character')),
                ('current_tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile')),
            ],
        ),
        migrations.CreateModel(
            name='Monster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('hp', models.PositiveIntegerField(default=1)),
                ('monster_type', models.CharField(choices=[('Goblin', 'Goblin'), ('Skeleton', 'Skeleton'), ('Slime', 'Slime'), ('Dragon', 'Dragon'), ('Troll', 'Troll'), ('Vampire', 'Vampire')], max_length=255)),
                ('attack', models.PositiveIntegerField(default=1)),
                ('tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile')),
            ],
        ),
        migrations.AddField(
            model_name='chest',
            name='tile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile'),
        ),
        migrations.AddField(
            model_name='character',
            name='current_tile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='character', to='api.tile'),
        ),
        migrations.AddField(
            model_name='character',
            name='world',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.world'),
        ),
    ]
