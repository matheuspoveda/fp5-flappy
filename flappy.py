import pygame, random, os
from pygame.locals import *

pygame.mixer.init()
point_sound = pygame.mixer.Sound('assets/audio/point.wav')
jumping_sound = pygame.mixer.Sound('assets/audio/wing.wav')
hit_sound = pygame.mixer.Sound('assets/audio/hit.wav')

BUTTON_WIDTH = 120
BUTTON_HEIGHT = 60

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 800

SPEED = 10
GRAVITY = 1
GAME_SPEED = 5

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500

PIPE_GAP = 200

player_missions = {
    5: False,
    15: False,
    30: False,
    50: False,
    75: False,
    100: False,
    150: False
}

player_coins = 0

bird_skins = {
    "bluebird": True,
    "redbird": False,
    "yellowbird": False
}

selected_skin = "bluebird"

class Checkbox:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.checked = False

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, (255, 255, 255), self.rect.topleft, self.rect.bottomright, 2)
            pygame.draw.line(screen, (255, 255, 255), self.rect.topright, self.rect.bottomleft, 2)

class Button:
    def __init__(self, text, x, y, width=225, height=50):
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.color = (255, 165, 0)
        self.enabled_color = (255, 140, 0)
        self.disabled_color = (100, 100, 100)
        self.selected_color = (0, 255, 0)

    def draw(self, screen, enabled=True, selected=False):
        if selected:
            color = self.selected_color
        else:
            color = self.enabled_color if enabled else self.disabled_color
        pygame.draw.rect(screen, color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Ground(pygame.sprite.Sprite): 
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.load_images(selected_skin)
        self.speed = SPEED
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 2
        self.rect[1] = SCREEN_HEIGHT / 2

    def load_images(self, bird_type):
        self.images = [pygame.image.load(f'assets/sprites/{bird_type}-upflap.png').convert_alpha(),
                       pygame.image.load(f'assets/sprites/{bird_type}-midflap.png').convert_alpha(),
                       pygame.image.load(f'assets/sprites/{bird_type}-downflap.png').convert_alpha()]

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)
        self.inverted = inverted
        self.scored = False
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 600)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP) 
    return (pipe, pipe_inverted)

BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

def get_player_name(screen):
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 25, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    set_name_button = Button("Setar nome", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 65)
    set_name_button_enabled = False
    
    explanation_text = font.render("Digite seu nome:", True, (255, 255, 255))
    explanation_rect = explanation_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if active:
                    if event.key == K_RETURN:
                        return text
                    elif event.key == K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                    set_name_button_enabled = bool(text)
                if event.key == K_TAB:
                    active = not active
                    color = color_active if active else color_inactive
            if event.type == MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                    color = color_active if active else color_inactive
                else:
                    active = False
                    color = color_inactive
                if set_name_button.rect.collidepoint(event.pos) and set_name_button_enabled:
                    return text
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if input_box.collidepoint(mouse_pos):
                    active = True
                    color = color_active
                else:
                    active = False
                    color = color_inactive

        screen.blit(BACKGROUND, (0, 0))
        pygame.draw.rect(screen, color, input_box, 2)
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        screen.blit(explanation_text, explanation_rect)
        set_name_button.draw(screen, enabled=set_name_button_enabled)
        pygame.display.flip()

color_scheme = "day"

player_scores = []

def save_scores(player_scores):
    with open('scores.txt', 'w') as file:
        for name, score in player_scores:
            file.write(f'{name},{score}\n')

def load_scores():
    if not os.path.exists('scores.txt'):
        return []
    
    player_scores = []
    with open('scores.txt', 'r') as file:
        for line in file:
            name, score = line.strip().split(',')
            player_scores.append((name, int(score)))
    return player_scores

def run_game(screen, player_name, checkboxes):
    global score, GAME_SPEED, color_scheme, BACKGROUND

    score = 0

    font = pygame.font.Font(None, 36)

    bird_group = pygame.sprite.Group()
    bird = Bird()
    bird_group.add(bird)

    ground_group = pygame.sprite.Group()
    for i in range(2):
        ground = Ground(GROUND_WIDTH * i)
        ground_group.add(ground)

    pipe_group = pygame.sprite.Group()
    for i in range(2):
        pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    clock = pygame.time.Clock()

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    bird.bump()
                    jumping_sound.play()

        screen.blit(BACKGROUND, (0, 0))

        if score >= 20 and color_scheme == "day":
            color_scheme = "night"
            BACKGROUND = pygame.image.load('assets/sprites/background-night.png')
            BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])
            new_ground = Ground(GROUND_WIDTH - 20)
            ground_group.add(new_ground)

        if is_off_screen(pipe_group.sprites()[0]):
            pipe_group.remove(pipe_group.sprites()[0])
            pipe_group.remove(pipe_group.sprites()[0])
            pipes = get_random_pipes(SCREEN_WIDTH * 2)
            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        bird_group.update()
        ground_group.update()
        pipe_group.update()
        bird_group.draw(screen)
        pipe_group.draw(screen)
        ground_group.draw(screen)
        for pipe in pipe_group:
            if not pipe.inverted and pipe.rect.right < SCREEN_WIDTH / 2 and not pipe.scored:
                point_sound.play()
                score += 1
                pipe.scored = True
                check_and_update_missions(score, checkboxes)

        score_text = font.render(f"Score: {score}", 1, (255, 255, 255))
        text_rect = score_text.get_rect(center=(SCREEN_WIDTH / 2, 15))
        screen.blit(score_text, text_rect)

        if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
            hit_sound.play()
            return player_name, score, checkboxes
        pygame.display.update()

def check_and_update_missions(score, checkboxes):
    global player_missions, player_coins
    for mission, completed in player_missions.items():
        if score >= mission and not completed:
            player_missions[mission] = True
            player_coins += 1
            update_missions_checkboxes(score, checkboxes)

def update_missions_checkboxes(player_score, checkboxes):
    missions_scores = [5, 15, 30, 50, 75, 100, 150]

    for i, mission_score in enumerate(missions_scores):
        if player_score >= mission_score:
            checkboxes[i].checked = True

def show_start_screen(screen):
    player_name = get_player_name(screen)
    show_home_screen(screen, player_name)

def show_instructions(screen):
    font = pygame.font.Font(None, 20)
    fonte = pygame.font.Font(None, 36)

    instructions_text = [
        "Como Jogar:",
        "Pressione a tecla ESPAÇO para fazer o pássaro saltar.",
        "Desvie dos canos voando para cima e para baixo.",
        "Se você colidir com o chão ou os canos, o jogo termina.",
        "Cada missao que voce consegue concluir te da 1 moeda.",
        "As moedas sao usadas para comprar novas cores na loja."
    ]

    screen.fill((0, 0, 0))
    screen.blit(BACKGROUND, (0, 0))
    
    instructions_title = fonte.render("Instruções", True, (255, 255, 255))
    instructions_title_rect = instructions_title.get_rect(center=(SCREEN_WIDTH / 2, 50))
    screen.blit(instructions_title, instructions_title_rect)

    line_height = 30
    text_y = (SCREEN_HEIGHT - (len(instructions_text) * line_height)) // 2

    for text in instructions_text:
        instruction = font.render(text, True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH / 2, text_y))
        screen.blit(instruction, instruction_rect)
        text_y += line_height

    back_button = Button("Voltar", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_button.rect.collidepoint(mouse_pos):
                    return

        back_button.draw(screen)
        pygame.display.update()

def show_home_screen(screen, player_name):
    start_button = Button("Iniciar", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    how_to_play_button = Button("Como Jogar", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 + 75)
    perfil_button = Button("Perfil", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 + 150)
    missões_button = Button("Missões", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 + 225)
    loja_button = Button("Loja", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 + 300)
    classificacao_button = Button("Classificação", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 + 375)
    quit_button = Button("Sair", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4 + 450)

    checkboxes = [Checkbox(SCREEN_WIDTH / 2 - 150, 150 + i * 40) for i in range(len(player_missions))]

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button.rect.collidepoint(mouse_pos):
                    player_name, score, checkboxes = run_game(screen, player_name, checkboxes)
                    player_name, score, checkboxes = show_end_screen(screen, player_name, score, checkboxes)
                elif how_to_play_button.rect.collidepoint(mouse_pos):
                    show_instructions(screen)
                elif perfil_button.rect.collidepoint(mouse_pos):
                    show_profile_screen(screen, player_name)
                elif missões_button.rect.collidepoint(mouse_pos):
                    show_missões_screen(screen, player_name, 0, checkboxes)
                elif loja_button.rect.collidepoint(mouse_pos):
                    show_loja_screen(screen, player_name)
                elif classificacao_button.rect.collidepoint(mouse_pos):
                    show_leaderboard_screen(screen)
                elif quit_button.rect.collidepoint(mouse_pos):
                    pygame.quit()

        screen.blit(BACKGROUND, (0, 0))
        start_button.draw(screen)
        how_to_play_button.draw(screen)
        perfil_button.draw(screen)
        missões_button.draw(screen)
        loja_button.draw(screen)
        classificacao_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.update()

def show_end_screen(screen, player_name, score, checkboxes):
    global player_scores
    
    restart_button = Button("Reiniciar", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 0)
    back_to_start_button = Button("Voltar para o Início", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150)
    missions_button = Button("Missões", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 75) 

    player_scores.append((player_name, score))
    save_scores(player_scores)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button.rect.collidepoint(mouse_pos):
                    return player_name, score, checkboxes
                elif back_to_start_button.rect.collidepoint(mouse_pos):
                    return player_name, score, checkboxes
                elif missions_button.rect.collidepoint(mouse_pos):
                    show_missões_screen(screen, player_name, score, checkboxes)

        screen.blit(BACKGROUND, (0, 0))
        restart_button.draw(screen)
        missions_button.draw(screen)
        back_to_start_button.draw(screen)
        pygame.display.update()

def draw_checkboxes(screen, checkboxes):
    for i, checkbox in enumerate(checkboxes):
        checkbox.draw(screen)        

def show_missões_screen(screen, player_name, player_score, checkboxes):
    font = pygame.font.Font(None, 36)
    back_button = Button("Voltar", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100)

    missions_descriptions = [
        "Alcançar 5 pontos",
        "Alcançar 15 pontos",
        "Alcançar 30 pontos",
        "Alcançar 50 pontos",
        "Alcançar 75 pontos",
        "Alcançar 100 pontos",
        "Alcançar 150 pontos"
    ]

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_button.rect.collidepoint(mouse_pos):
                    return player_name, player_score, checkboxes

        screen.fill((0, 0, 0))
        screen.blit(BACKGROUND, (0, 0))
        missões_title = font.render("Missões", True, (255, 255, 255))
        missões_title_rect = missões_title.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(missões_title, missões_title_rect)

        draw_checkboxes(screen, checkboxes)

        for i, checkbox in enumerate(checkboxes):
            mission_text = font.render(missions_descriptions[i], True, (255, 255, 255))
            mission_text_rect = mission_text.get_rect(midleft=(checkbox.rect.right + 10, checkbox.rect.centery))
            screen.blit(mission_text, mission_text_rect)

        back_button.draw(screen)
        pygame.display.update()

def show_profile_screen(screen, player_name):
    screen.blit(BACKGROUND, (0, 0))
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 25, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    new_name = player_name

    alterar_button = Button("Alterar Nome", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 65)
    voltar_button = Button("Voltar", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 140)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                if alterar_button.rect.collidepoint(event.pos):
                    player_name = new_name
                elif voltar_button.rect.collidepoint(event.pos):
                    show_home_screen(screen, player_name)
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    player_name = new_name
                elif event.key == K_BACKSPACE:
                    new_name = new_name[:-1]
                else:
                    new_name += event.unicode
                active = True

        screen.fill((30, 30, 30))
        screen.blit(BACKGROUND, (0, 0))
        text_surface = font.render("Nome atual:", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        screen.blit(text_surface, text_rect)

        input_box.w = max(200, text_surface.get_width() + 10)
        pygame.draw.rect(screen, color, input_box, 2)
        text_surface = font.render(new_name, True, (255, 255, 255))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

        alterar_button.draw(screen)
        voltar_button.draw(screen)

        pygame.display.flip()

def show_leaderboard_screen(screen):
    global player_scores
    player_scores = load_scores()
    sorted_scores = sorted(player_scores, key=lambda x: x[1], reverse=True)

    font = pygame.font.Font(None, 36)
    back_button = Button("Voltar", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_button.rect.collidepoint(mouse_pos):
                    return

        screen.fill((0, 0, 0))
        screen.blit(BACKGROUND, (0, 0))
        leaderboard_title = font.render("Classificação - Top 5", True, (255, 255, 255))
        leaderboard_title_rect = leaderboard_title.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(leaderboard_title, leaderboard_title_rect)

        for i, (name, score) in enumerate(sorted_scores[:5]):
            score_text = font.render(f"{i + 1}. {name}: {score}", True, (255, 255, 255))
            score_text_rect = score_text.get_rect(center=(SCREEN_WIDTH / 2, 150 + i * 40))
            screen.blit(score_text, score_text_rect)

        back_button.draw(screen)
        pygame.display.update()

def show_loja_screen(screen, player_name):
    global player_coins, bird_skins, selected_skin
    font = pygame.font.Font(None, 36)
    back_button = Button("Voltar", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100)

    bird_options = ["bluebird", "redbird", "yellowbird"]
    bird_prices = {"redbird": 5, "yellowbird": 10}
    bird_buttons = [Button(bird, SCREEN_WIDTH / 2, 250 + i * 100) for i, bird in enumerate(bird_options)]

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_button.rect.collidepoint(mouse_pos):
                    return
                for i, bird_button in enumerate(bird_buttons):
                    if bird_button.rect.collidepoint(mouse_pos):
                        selected_bird = bird_options[i]
                        if bird_skins[selected_bird]:
                            selected_skin = selected_bird
                        elif player_coins >= bird_prices.get(selected_bird, 0):
                            player_coins -= bird_prices[selected_bird]
                            bird_skins[selected_bird] = True
                            selected_skin = selected_bird

        screen.fill((0, 0, 0))
        screen.blit(BACKGROUND, (0, 0))
        loja_title = font.render("Loja", True, (255, 255, 255))
        loja_title_rect = loja_title.get_rect(center=(SCREEN_WIDTH / 2, 100))
        screen.blit(loja_title, loja_title_rect)

        coins_text = font.render(f"Moedas: {player_coins}", True, (255, 255, 255))
        coins_text_rect = coins_text.get_rect(center=(SCREEN_WIDTH / 2, 150))
        screen.blit(coins_text, coins_text_rect)

        for i, bird_button in enumerate(bird_buttons):
            bird_button.draw(screen, selected=(selected_skin == bird_options[i]))
            if bird_skins[bird_options[i]]:
                owned_text = font.render("Comprado", True, (0, 255, 0))
                owned_text_rect = owned_text.get_rect(center=(bird_button.rect.centerx, bird_button.rect.centery + 40))
                screen.blit(owned_text, owned_text_rect)
            elif bird_options[i] != "bluebird":
                price_text = font.render(f"Preço: {bird_prices[bird_options[i]]} moedas", True, (255, 0, 0))
                price_text_rect = price_text.get_rect(center=(bird_button.rect.centerx, bird_button.rect.centery + 40))
                screen.blit(price_text, price_text_rect)

        back_button.draw(screen)
        pygame.display.update()

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
show_start_screen(screen)