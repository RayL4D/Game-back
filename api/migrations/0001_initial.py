# Generated by Django 5.0.6 on 2025-01-20 13:01

import datetime
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
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('item_type', models.CharField(choices=[('ITMT_00001', 'ITMT_00001'), ('ITMT_00002', 'ITMT_00002'), ('ITMT_00003', 'ITMT_00003'), ('ITMT_00004', 'ITMT_00004'), ('ITMT_00005', 'ITMT_00005'), ('ITMT_00006', 'ITMT_00006'), ('ITMT_00007', 'ITMT_00007'), ('ITMT_00008', 'ITMT_00008'), ('ITMT_00009', 'ITMT_00009')], max_length=255)),
                ('is_equipped', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
                ('attack_power', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('defense', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('healing', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
                ('starting_map', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='NPC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('hp', models.PositiveIntegerField(default=1)),
                ('is_dead', models.BooleanField(default=False)),
                ('species', models.CharField(choices=[('NPCS_00001', 'NPCS_00001'), ('NPCS_00002', 'NPCS_00002'), ('NPCS_00003', 'NPCS_00003'), ('NPCS_00004', 'NPCS_00004'), ('NPCS_00005', 'NPCS_00005'), ('NPCS_00006', 'NPCS_00006'), ('NPCS_00007', 'NPCS_00007'), ('NPCS_00008', 'NPCS_00008'), ('NPCS_00009', 'NPCS_00009')], max_length=255)),
                ('role', models.CharField(max_length=255)),
                ('behaviour', models.CharField(choices=[('NPCB_00002', 'NPCB_00002'), ('NPCB_00003', 'NPCB_00003'), ('NPCB_00001', 'NPCB_00001')], max_length=255)),
                ('attack_power', models.PositiveIntegerField(default=1)),
                ('defense', models.PositiveIntegerField(default=1)),
                ('experience', models.PositiveIntegerField(default=10)),
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
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('attack_power', models.PositiveIntegerField(default=1)),
                ('defense', models.PositiveIntegerField(default=1)),
                ('hp', models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)])),
                ('experience', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('character_class', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.characterclass')),
                ('session_key', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sessions.session')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CharacterInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('is_equipped', models.BooleanField(default=False)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.game')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.item')),
                ('primary_weapon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipped_as_primary_weapon', to='api.item')),
                ('secondary_weapon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipped_as_secondary_weapon', to='api.item')),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='inventory',
            field=models.ManyToManyField(through='api.CharacterInventory', to='api.item'),
        ),
        migrations.AddField(
            model_name='game',
            name='map',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.map'),
        ),
        migrations.CreateModel(
            name='Dialogue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.game')),
                ('NPC', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.npc')),
            ],
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
                ('level', models.PositiveIntegerField(default=1)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.game')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.skill')),
            ],
        ),
        migrations.CreateModel(
            name='Tile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posX', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('posY', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('visited', models.BooleanField(default=False)),
                ('east_door', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='east_connected_tile', to='api.tile')),
                ('map', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.map')),
                ('north_door', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='north_connected_tile', to='api.tile')),
                ('portal_to_map', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portal_tiles', to='api.map')),
                ('south_door', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='south_connected_tile', to='api.tile')),
                ('west_door', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='west_connected_tile', to='api.tile')),
            ],
        ),
        migrations.AddField(
            model_name='shop',
            name='tile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile'),
        ),
        migrations.CreateModel(
            name='NPCSavedState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hp', models.IntegerField()),
                ('behaviour', models.CharField(choices=[('NPCB_00002', 'NPCB_00002'), ('NPCB_00003', 'NPCB_00003'), ('NPCB_00001', 'NPCB_00001')], max_length=255)),
                ('is_dead', models.BooleanField(default=False)),
                ('npc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.npc')),
                ('tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile')),
            ],
        ),
        migrations.AddField(
            model_name='npc',
            name='tile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile'),
        ),
        migrations.AddField(
            model_name='game',
            name='current_tile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='game', to='api.tile'),
        ),
        migrations.CreateModel(
            name='TileSavedState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visited', models.BooleanField(default=False)),
                ('tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile')),
            ],
        ),
    ]
