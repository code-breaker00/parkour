from panda3d.core import *
from panda3d.core import loadPrcFileData

# Fix pour Panda3D : forcer le bon affichage
loadPrcFileData('', 'load-display pandagl')
loadPrcFileData('', 'win-size 1280 720')
loadPrcFileData('', 'fullscreen 0')
loadPrcFileData('', 'window-title Parkour Infini')

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import webbrowser

app = Ursina()
window.title = "Parkour Infini"
window.color = color.rgb(160, 210, 255)  # Bleu ciel clair
window.borderless = False
window.fullscreen = False

credits_panel = None
player = None
death_screen = None
menu_panel = None
platform_entities = []
goal_entity = None
start_block = None
menu_background = Entity(parent=camera.ui)
background_hue = 0
level_score = 0
loading = False

# ========== UI ==========
def create_main_menu():
    global menu_panel
    menu_panel = Entity(parent=camera.ui, enabled=True)
    Panel(scale=(0.6, 0.6), color=color.rgba(0, 0, 0, 180), parent=menu_panel)
    Text("Parkour Infini", parent=menu_panel, y=0.2, scale=2, origin=(0, 0), color=color.azure)
    Button(text="JOUER", parent=menu_panel, scale=(0.3, 0.1), y=0.1, on_click=start_game)
    Button(text="CRÉDITS", parent=menu_panel, scale=(0.3, 0.1), y=-0.05, on_click=show_credits)
    Button(text="QUITTER", parent=menu_panel, scale=(0.3, 0.1), y=-0.2, on_click=application.quit)


def create_death_screen():
    global death_screen
    death_screen = Entity(parent=camera.ui, enabled=False)
    Panel(scale=(0.5, 0.4), color=color.rgba(0, 0, 0, 200), parent=death_screen)
    Text("Tu es mort", scale=2, y=0.1, parent=death_screen, origin=(0, 0), color=color.red)
    Button(text="Recommencer", scale=(0.3, 0.1), y=-0.1, parent=death_screen, on_click=respawn_player)

score_text = Text("Niveau : 0", position=(-0.85, 0.45), scale=1.5, color=color.black)  # Texte noir
author_text = Text("created by code_breaker", position=(-0.85, 0.40), scale=1, color=color.black)

def hide_credits():
    global credits_panel
    if credits_panel:
        destroy(credits_panel)
    menu_panel.enabled = True


def show_credits():
    global credits_panel
    menu_panel.enabled = False

    credits_panel = Entity(parent=camera.ui)
    Panel(scale=(0.6, 0.6), color=color.rgba(0, 0, 0, 180), parent=credits_panel)

    Text("Crédits", parent=credits_panel, y=0.2, scale=2, origin=(0, 0), color=color.azure)
    Text(text="mes reseaux", parent=credits_panel, y=0.10, scale=1.2, origin=(0, 0), color=color.white)
    Button(
        text="https://guns.lol/code_breaker",
        parent=credits_panel,
        y=0.05,
        scale=(0.5, 0.05),
        on_click=lambda: webbrowser.open("https://guns.lol/code_breaker")
    )

    Text(text="mon github", parent=credits_panel, y=-0.05, scale=1.2, origin=(0, 0), color=color.white)

    Button(
        text="https://github.com/code_breaker00",
        parent=credits_panel,
        y=-0.12,
        scale=(0.5, 0.05),
        on_click=lambda: webbrowser.open("https://github.com/code-breaker00")
    )

    Text("discord : code_breaker0", parent=credits_panel, y=-0.22, scale=1.1, origin=(0, 0), color=color.white)

    Button(
        text="RETOUR",
        parent=credits_panel,
        y=-0.35,
        scale=(0.3, 0.07),
        on_click=hide_credits
    )


# ========== LOGIQUE ==========
def start_game():
    global level_score
    level_score = 0
    update_score()
    menu_panel.enabled = False
    death_screen.enabled = False
    generate_level()

def update_score():
    score_text.text = f"Niveau : {level_score}"

def generate_level():
    global platform_entities, goal_entity, start_block, player
    destroy_all_platforms()

    # Bloc de départ
    spawn_pos = Vec3(0, 2, 0)
    start_block = Entity(model='cube', color=color.blue, position=(0, 0, 0), scale=(2, 0.5, 2), collider='box')
    platform_entities.append(start_block)

    # Génération des plateformes
    pos = Vec3(0, 0, 0)
    platform_count = 6 + level_score * 2

    for i in range(platform_count):
        dx = random.randint(4, 6 + level_score)
        dy = random.randint(-1, 1)
        dz = random.randint(-2, 2)
        pos += Vec3(dx, dy, dz)
        p = Entity(model='cube', color=color.gray, position=pos, scale=(2, 0.5, 2), collider='box')
        platform_entities.append(p)

    # Bloc d’arrivée (goal)
    goal_pos = pos + Vec3(4, 0, 0)
    goal_entity = Entity(
        model='cube',
        color=color.green,
        position=goal_pos,
        scale=(2, 0.5, 2),
        collider='box',
        name='goal'
    )
    platform_entities.append(goal_entity)

    # Création du joueur
    if player:
        destroy(player)
    create_player(spawn_pos)

def create_player(spawn_pos):
    global player
    player = FirstPersonController()
    player.gravity = 1
    player.jump_height = 5  # saut plus haut
    player.speed = 10       # vitesse plus rapide
    player.cursor.visible = False
    player.position = spawn_pos
    player.collider = BoxCollider(player, size=Vec3(1, 2, 1))

def destroy_all_platforms():
    global platform_entities, goal_entity, start_block
    for p in platform_entities:
        destroy(p)
    platform_entities.clear()
    if goal_entity:
        destroy(goal_entity)
        goal_entity = None
    if start_block:
        destroy(start_block)
        start_block = None

def respawn_player():
    if start_block:
        player.position = start_block.position + Vec3(0, 2, 0)
        player.enabled = True
        death_screen.enabled = False

def go_to_next_level():
    global loading, level_score
    if not loading:
        loading = True
        invoke(load_next_level, delay=2)
        player.position = start_block.position + Vec3(0, 2, 0)

def load_next_level():
    global level_score, loading
    level_score += 1
    update_score()
    generate_level()
    loading = False

# ========== ANIMATION DE FOND ==========
def animate_menu_background():
    global background_hue
    background_hue += time.dt * 10
    if background_hue > 360:
        background_hue = 0
    menu_background.color = color.hsv(background_hue, 0.3, 0.8)

# ========== LANCEMENT ==========
create_main_menu()
create_death_screen()

# ========== UPDATE LOOP ==========
def update():
    animate_menu_background()

    if player and player.enabled:
        if player.y < -10:
            player.enabled = False
            death_screen.enabled = True

        hit = player.intersects()
        if hit.hit and hit.entity.name == 'goal':
            print("🟢 Tu as touché la brique verte !")
            go_to_next_level()

    if held_keys['escape'] and not menu_panel.enabled:
        menu_panel.enabled = True
        death_screen.enabled = False
        if player:
            destroy(player)
        destroy_all_platforms()
        camera.parent = scene
        camera.position = (0, 0, -20)
        camera.rotation = (0, 0, 0)

app.run()
