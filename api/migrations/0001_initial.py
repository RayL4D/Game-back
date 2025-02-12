# Generated by Django 5.0.6 on 2025-02-12 13:09

import datetime
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
                ('type', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('attack_power', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('defense', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('healing', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('bodypart', models.CharField(blank=True, max_length=5, null=True)),
                ('bodypart_lock', models.CharField(blank=True, max_length=5, null=True)),
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
                ('experience_reward', models.PositiveIntegerField(default=1)),
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
                ('experience', models.PositiveIntegerField(default=1)),
                ('level', models.PositiveIntegerField(default=1)),
                ('skill_points', models.IntegerField(default=0)),
                ('bronze', models.PositiveIntegerField(default=0)),
                ('silver', models.PositiveIntegerField(default=0)),
                ('gold', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('character_class', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.characterclass')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
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
            name='CharacterInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locked_slots', models.JSONField(default=dict)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.game')),
                ('bag', models.ManyToManyField(related_name='character_inventory', to='api.item')),
                ('boots', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipped_as_boots', to='api.item')),
                ('chestplate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipped_as_chestplate', to='api.item')),
                ('helmet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipped_as_helmet', to='api.item')),
                ('leggings', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipped_as_leggings', to='api.item')),
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
        migrations.AddField(
            model_name='game',
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
                ('north_door_level', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('south_door_level', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('east_door_level', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('west_door_level', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('map', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.map')),
                ('portal_destination_tile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='arrival_tiles', to='api.tile')),
                ('portal_to_map', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portal_tiles', to='api.map')),
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
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.game')),
                ('npc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.npc')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile')),
            ],
        ),
        migrations.AddField(
            model_name='npc',
            name='tile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile'),
        ),
        migrations.CreateModel(
            name='ItemSavedState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.game')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile')),
            ],
        ),
        migrations.AddField(
            model_name='item',
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
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.game')),
                ('tile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('game', 'user', 'tile')},
            },
        ),
    ]
