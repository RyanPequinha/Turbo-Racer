"""
╔══════════════════════════════════════════════════════════╗
║           🏎  TURBO RACER  —  Jogo de Corrida           ║
║          Desenvolvido com Python + Pygame                ║
║                                                          ║
║  Controles:                                              ║
║    Teclado : A/← esq | D/→ dir | W/↑ acelera | S/↓ freia║
║    Mouse   : Clique e arraste o carro lateralmente       ║
║                                                          ║
║  Para jogar:                                             ║
║    pip install pygame                                    ║
║    python corrida_pygame.py                              ║
╚══════════════════════════════════════════════════════════╝
"""

import pygame
import random
import math
import sys
import os

# ─────────────────────────────────────────────────────────
#  CONFIGURAÇÕES GERAIS
# ─────────────────────────────────────────────────────────
LARGURA, ALTURA = 480, 720      # Resolução da janela
FPS = 60                         # Quadros por segundo
TITULO = "Turbo Racer 🏎"

# Largura da pista e posição X do centro
PISTA_ESQUERDA = 60             # Borda esquerda da pista
PISTA_DIREITA  = 420            # Borda direita da pista
PISTA_CENTRO   = (PISTA_ESQUERDA + PISTA_DIREITA) // 2

# Cores
PRETO       = (0,   0,   0)
BRANCO      = (255, 255, 255)
CINZA_ESCURO= (30,  30,  30)
CINZA       = (80,  80,  80)
CINZA_CLARO = (150, 150, 150)
VERMELHO    = (220, 40,  40)
VERMELHO_ESC= (140, 20,  20)
AZUL        = (40,  100, 220)
AZUL_CLARO  = (100, 160, 255)
VERDE       = (40,  180, 60)
VERDE_CLARO = (80,  220, 100)
AMARELO     = (255, 220, 0)
LARANJA     = (255, 140, 0)
ROXO        = (160, 40,  200)
ROXO_CLARO  = (200, 100, 255)
CIANO       = (0,   220, 220)
BEGE        = (200, 180, 120)

# Fundo (deserto)
COR_FUNDO   = (180, 145, 90)    # areia
COR_PISTA   = (50,  50,  50)    # asfalto
COR_CALÇADA = (100, 85,  60)    # calçada de terra

# ─────────────────────────────────────────────────────────
#  UTILITÁRIOS DE DESENHO
# ─────────────────────────────────────────────────────────

def desenha_carro(surf, x, y, largura, altura, cor_corpo, cor_detalhe,
                  cor_vidro=None, espelhado=False):
    """
    Desenha um carro estilizado (visão de cima) com carroceria,
    janelas e rodas, centrado em (x, y).
    espelhado=True para carros inimigos (frente voltada para baixo).
    """
    if cor_vidro is None:
        cor_vidro = AZUL_CLARO

    hw = largura // 2
    hh = altura  // 2

    # — Sombra
    sombra = pygame.Surface((largura + 8, altura + 8), pygame.SRCALPHA)
    pygame.draw.rect(sombra, (0, 0, 0, 60),
                     (0, 0, largura + 8, altura + 8), border_radius=10)
    surf.blit(sombra, (x - hw + 2, y - hh + 4))

    # — Carroceria principal
    corpo_rect = pygame.Rect(x - hw, y - hh, largura, altura)
    pygame.draw.rect(surf, cor_corpo, corpo_rect, border_radius=8)

    # — Teto / janela central
    jan_w = int(largura * 0.55)
    jan_h = int(altura  * 0.35)
    jan_rect = pygame.Rect(x - jan_w // 2, y - jan_h // 2, jan_w, jan_h)
    pygame.draw.rect(surf, cor_vidro, jan_rect, border_radius=5)

    # — Para-brisa (frente): na parte de cima se normal, baixo se espelhado
    pb_w = int(largura * 0.60)
    pb_h = 10
    if not espelhado:
        pb_y = y - hh + 8
    else:
        pb_y = y + hh - 8 - pb_h
    pb_rect = pygame.Rect(x - pb_w // 2, pb_y, pb_w, pb_h)
    pygame.draw.rect(surf, cor_vidro, pb_rect, border_radius=4)

    # — Faixa decorativa (stripe)
    stripe_rect = pygame.Rect(x - 4, y - hh, 8, altura)
    pygame.draw.rect(surf, cor_detalhe, stripe_rect)

    # — Rodas (4 cantos)
    roda_w, roda_h = 10, 16
    offsets = [(-hw - 2, -hh + 8), (hw - roda_w + 2, -hh + 8),
               (-hw - 2, hh - roda_h - 8), (hw - roda_w + 2, hh - roda_h - 8)]
    for ox, oy in offsets:
        r = pygame.Rect(x + ox, y + oy, roda_w, roda_h)
        pygame.draw.rect(surf, PRETO, r, border_radius=3)
        pygame.draw.rect(surf, CINZA_CLARO,
                         r.inflate(-4, -4), border_radius=2)

    # — Contorno
    pygame.draw.rect(surf, cor_detalhe, corpo_rect, width=2, border_radius=8)


def desenha_powerup(surf, x, y, tipo, raio=18):
    """Desenha ícone de power-up (turbo=amarelo, escudo=ciano)."""
    if tipo == "turbo":
        cor = AMARELO
        simbolo = "⚡"
    else:
        cor = CIANO
        simbolo = "🛡"

    # Círculo brilhante
    pygame.draw.circle(surf, cor, (x, y), raio)
    pygame.draw.circle(surf, BRANCO, (x, y), raio, 2)
    # Símbolo interno desenhado como forma geométrica
    if tipo == "turbo":
        pts = [(x, y - 10), (x - 6, y + 2), (x, y - 2), (x, y + 10),
               (x + 6, y - 2), (x, y + 2)]
        pygame.draw.polygon(surf, BRANCO, pts)
    else:
        pygame.draw.circle(surf, BRANCO, (x, y), raio - 6, 3)


# ─────────────────────────────────────────────────────────
#  PARTÍCULA
# ─────────────────────────────────────────────────────────

class Particula:
    """
    Pequena partícula de explosão/fumaça.
    Criada ao colidir; some gradualmente.
    """
    def __init__(self, x, y, cor=None):
        self.x = x + random.uniform(-20, 20)
        self.y = y + random.uniform(-20, 20)
        angulo = random.uniform(0, 2 * math.pi)
        vel = random.uniform(1, 5)
        self.vx = math.cos(angulo) * vel
        self.vy = math.sin(angulo) * vel
        self.raio = random.randint(4, 10)
        self.vida = random.randint(20, 45)
        self.vida_max = self.vida
        self.cor = cor or random.choice([VERMELHO, LARANJA, AMARELO, BRANCO])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1            # gravidade leve
        self.vida -= 1
        self.raio = max(1, self.raio - 0.1)

    def draw(self, surf):
        alpha = int(255 * (self.vida / self.vida_max))
        cor = (*self.cor[:3], alpha)
        s = pygame.Surface((self.raio * 2, self.raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, cor, (self.raio, self.raio), self.raio)
        surf.blit(s, (int(self.x) - self.raio, int(self.y) - self.raio))

    @property
    def morta(self):
        return self.vida <= 0


# ─────────────────────────────────────────────────────────
#  CARRO INIMIGO
# ─────────────────────────────────────────────────────────

class Inimigo:
    """
    Carro adversário que surge no topo e desce em direção ao jogador.
    Velocidade e cor são aleatórias dentro de limites.
    """
    CORES = [
        (VERMELHO,     VERMELHO_ESC),
        (ROXO,         ROXO_CLARO),
        (VERDE,        VERDE_CLARO),
        (LARANJA,      AMARELO),
        (AZUL,         AZUL_CLARO),
        (BRANCO,       CINZA_CLARO),
    ]

    def __init__(self, vel_base):
        self.w = 36
        self.h = 60
        # Posiciona em uma faixa aleatória dentro da pista
        margem = self.w
        self.x = random.randint(PISTA_ESQUERDA + margem, PISTA_DIREITA - margem)
        self.y = -self.h
        # Velocidade um pouco acima ou abaixo da base
        self.vel = vel_base + random.uniform(-1.5, 2.5)
        self.vel = max(2, self.vel)
        self.cor_corpo, self.cor_det = random.choice(self.CORES)
        self.rect = pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                                self.w, self.h)
        self.passou = False         # flag: passou pelo jogador sem bater

    def update(self, scroll_speed):
        """Atualiza posição descendo conforme o scroll + velocidade própria."""
        self.y += scroll_speed + self.vel
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surf):
        desenha_carro(surf, int(self.x), int(self.y),
                      self.w, self.h,
                      self.cor_corpo, self.cor_det,
                      cor_vidro=(200, 230, 255),
                      espelhado=True)

    @property
    def fora(self):
        return self.y > ALTURA + self.h


# ─────────────────────────────────────────────────────────
#  POWER-UP
# ─────────────────────────────────────────────────────────

class PowerUp:
    """
    Objeto coletável que aparece aleatoriamente na pista.
    Tipos: "turbo" (velocidade extra) ou "escudo" (imunidade breve).
    """
    def __init__(self, vel_scroll):
        self.tipo = random.choice(["turbo", "escudo"])
        self.x = random.randint(PISTA_ESQUERDA + 30, PISTA_DIREITA - 30)
        self.y = -30
        self.vel = vel_scroll
        self.raio = 18
        self.rect = pygame.Rect(self.x - self.raio, self.y - self.raio,
                                self.raio * 2, self.raio * 2)
        # Animação de pulso
        self.pulso = 0

    def update(self, vel_scroll):
        self.y += vel_scroll + 1
        self.rect.center = (self.x, int(self.y))
        self.pulso += 0.1

    def draw(self, surf):
        r = self.raio + int(math.sin(self.pulso) * 3)
        desenha_powerup(surf, self.x, int(self.y), self.tipo, r)

    @property
    def fora(self):
        return self.y > ALTURA + 40


# ─────────────────────────────────────────────────────────
#  SONS (GERADOS PROGRAMATICAMENTE SEM ARQUIVO EXTERNO)
# ─────────────────────────────────────────────────────────

def gera_som_colisao():
    """Gera som de explosão/batida via síntese de ruído."""
    import numpy as np
    taxa = 44100
    duracao = 0.35
    amostras = int(taxa * duracao)
    t = np.linspace(0, duracao, amostras, False)
    ruido = np.random.uniform(-1, 1, amostras)
    envelope = np.exp(-t * 12)
    onda = (ruido * envelope * 32767).astype(np.int16)
    stereo = np.column_stack([onda, onda])
    return pygame.sndarray.make_sound(stereo)


def gera_som_powerup():
    """Gera som de coleta de power-up (sine sweep ascendente)."""
    import numpy as np
    taxa = 44100
    duracao = 0.25
    amostras = int(taxa * duracao)
    t = np.linspace(0, duracao, amostras, False)
    freq = np.linspace(400, 1200, amostras)
    onda = np.sin(2 * np.pi * freq * t)
    envelope = np.exp(-t * 6)
    onda = (onda * envelope * 28000).astype(np.int16)
    stereo = np.column_stack([onda, onda])
    return pygame.sndarray.make_sound(stereo)


def gera_som_motor():
    """Gera loop de som de motor (ruído grave pulsante)."""
    import numpy as np
    taxa = 44100
    duracao = 0.5
    amostras = int(taxa * duracao)
    t = np.linspace(0, duracao, amostras, False)
    base = np.sin(2 * np.pi * 80 * t) * 0.6
    harmonico = np.sin(2 * np.pi * 160 * t) * 0.3
    ruido = np.random.uniform(-0.1, 0.1, amostras)
    onda = ((base + harmonico + ruido) * 8000).astype(np.int16)
    stereo = np.column_stack([onda, onda])
    return pygame.sndarray.make_sound(stereo)


# ─────────────────────────────────────────────────────────
#  JOGO PRINCIPAL
# ─────────────────────────────────────────────────────────

class JogoCorrida:
    """
    Classe principal que gerencia todos os estados do jogo:
    INICIO → JOGANDO → GAME_OVER
    """

    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO)
        self.clock = pygame.time.Clock()

        # Carrega fontes
        self.fonte_titulo  = pygame.font.SysFont("Arial Black", 52, bold=True)
        self.fonte_grande  = pygame.font.SysFont("Arial Black", 36, bold=True)
        self.fonte_media   = pygame.font.SysFont("Arial",        22, bold=True)
        self.fonte_pequena = pygame.font.SysFont("Arial",        16)
        self.fonte_hud     = pygame.font.SysFont("Courier New",  18, bold=True)

        # Tenta carregar sons (falha silenciosamente se numpy não instalado)
        self.som_colisao = None
        self.som_powerup = None
        self.som_motor   = None
        try:
            self.som_colisao = gera_som_colisao()
            self.som_colisao.set_volume(0.7)
            self.som_powerup = gera_som_powerup()
            self.som_powerup.set_volume(0.5)
            self.som_motor = gera_som_motor()
            self.som_motor.set_volume(0.15)
        except Exception:
            pass  # sem numpy → sem som, jogo continua normalmente

        self.estado = "INICIO"
        self.reset()

    # ──────────────────────────────────────────
    #  RESET — Reinicia todas as variáveis
    # ──────────────────────────────────────────
    def reset(self):
        # Jogador
        self.jogador_x    = float(PISTA_CENTRO)
        self.jogador_y    = float(ALTURA - 120)
        self.jogador_w    = 40
        self.jogador_h    = 68
        self.jogador_vel  = 0.0       # velocidade horizontal
        self.vel_scroll   = 4.0       # velocidade da estrada (sobe com dificuldade)
        self.aceleracao   = 6.0       # km/h exibido = base + ganho
        self.velocidade_kmh = 60

        # Controle por mouse
        self.arrastando    = False
        self.arrasto_offset= 0.0

        # Pontuação e tempo
        self.pontos        = 0
        self.tempo_jogo    = 0         # frames
        self.proximo_nivel = 600       # frames para próxima dificuldade
        self.nivel         = 1

        # Vida / colisão
        self.vidas         = 3
        self.invencivel    = 0         # frames de invencibilidade após bater
        self.tremor        = 0         # frames de tremor de câmera
        self.tremor_amp    = 0

        # Escudo
        self.escudo_ativo  = 0         # frames restantes
        self.turbo_ativo   = 0         # frames restantes

        # Inimigos e power-ups
        self.inimigos      = []
        self.powerups      = []
        self.particulas    = []

        # Timer de spawn
        self.spawn_timer   = 0
        self.spawn_intervalo = 90      # frames entre spawns
        self.spawn_pu_timer= 0
        self.spawn_pu_intervalo = 400

        # Animação da estrada (linhas)
        self.offset_estrada = 0.0

        # Fundo (cactos no deserto)
        self.objetos_fundo = self._gera_fundo()

        # Motor
        if self.som_motor:
            self.som_motor.play(-1)    # loop infinito

    # ──────────────────────────────────────────
    #  GERA OBJETOS DECORATIVOS DO FUNDO
    # ──────────────────────────────────────────
    def _gera_fundo(self):
        """Cria lista de cactos/arbustos aleatórios nas laterais."""
        objs = []
        for _ in range(18):
            lado = random.choice(["esq", "dir"])
            x = random.randint(5, PISTA_ESQUERDA - 10) if lado == "esq" \
                else random.randint(PISTA_DIREITA + 5, LARGURA - 10)
            y = random.randint(0, ALTURA)
            tipo = random.choice(["cacto", "arbusto", "pedra"])
            tam = random.randint(12, 28)
            objs.append({"x": x, "y": y, "tipo": tipo, "tam": tam})
        return objs

    # ──────────────────────────────────────────
    #  LOOP PRINCIPAL
    # ──────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self._eventos()

            if self.estado == "INICIO":
                self._tela_inicio()
            elif self.estado == "JOGANDO":
                self._update()
                self._desenhar()
            elif self.estado == "GAME_OVER":
                self._tela_game_over()

            pygame.display.flip()

    # ──────────────────────────────────────────
    #  EVENTOS (teclado + mouse)
    # ──────────────────────────────────────────
    def _eventos(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Tela inicial: qualquer tecla inicia
            if self.estado == "INICIO" and ev.type == pygame.KEYDOWN:
                self.estado = "JOGANDO"

            # Game over: R reinicia, ESC sai
            if self.estado == "GAME_OVER":
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:
                        self.reset()
                        self.estado = "JOGANDO"
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # Controle por mouse (arrastar carro)
            if self.estado == "JOGANDO":
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    # Verifica se clicou sobre o carro do jogador
                    rect_jog = pygame.Rect(
                        self.jogador_x - self.jogador_w // 2,
                        self.jogador_y - self.jogador_h // 2,
                        self.jogador_w, self.jogador_h)
                    if rect_jog.collidepoint(mx, my):
                        self.arrastando = True
                        self.arrasto_offset = self.jogador_x - mx

                if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                    self.arrastando = False

                if ev.type == pygame.MOUSEMOTION and self.arrastando:
                    mx, _ = ev.pos
                    # Move o carro mantendo o offset do clique inicial
                    novo_x = mx + self.arrasto_offset
                    self.jogador_x = max(PISTA_ESQUERDA + self.jogador_w // 2,
                                        min(PISTA_DIREITA  - self.jogador_w // 2,
                                            novo_x))

    # ──────────────────────────────────────────
    #  UPDATE — lógica a cada frame
    # ──────────────────────────────────────────
    def _update(self):
        self.tempo_jogo += 1

        # —— Aumento de dificuldade ——
        if self.tempo_jogo >= self.proximo_nivel:
            self.proximo_nivel += 600
            self.nivel += 1
            self.vel_scroll       = min(14, self.vel_scroll + 0.8)
            self.spawn_intervalo  = max(30, self.spawn_intervalo - 8)
            self.aceleracao       = min(12, self.aceleracao + 0.5)

        # —— Velocidade exibida em km/h ——
        base_kmh = 60 + self.nivel * 15
        if self.turbo_ativo > 0:
            self.velocidade_kmh = min(260, base_kmh + 80)
        else:
            self.velocidade_kmh = base_kmh

        # —— Scroll da estrada ——
        scroll_real = self.vel_scroll * (2.0 if self.turbo_ativo > 0 else 1.0)
        self.offset_estrada = (self.offset_estrada + scroll_real) % 60

        # —— Scroll dos objetos de fundo ——
        for obj in self.objetos_fundo:
            obj["y"] += scroll_real * 0.7
            if obj["y"] > ALTURA + 40:
                obj["y"] = -40
                lado = random.choice(["esq", "dir"])
                obj["x"] = random.randint(5, PISTA_ESQUERDA - 10) if lado == "esq" \
                    else random.randint(PISTA_DIREITA + 5, LARGURA - 10)

        # —— Controle por teclado ——
        if not self.arrastando:
            teclas = pygame.key.get_pressed()
            accel = 6.0
            if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
                self.jogador_vel = max(-accel, self.jogador_vel - 1.2)
            elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
                self.jogador_vel = min(accel, self.jogador_vel + 1.2)
            else:
                # Fricção: desacelera horizontalmente
                self.jogador_vel *= 0.8

            # Turbo pelo teclado
            if (teclas[pygame.K_w] or teclas[pygame.K_UP]) and self.turbo_ativo == 0:
                # Só ativa turbo se houver carga
                pass  # turbo só via power-up
            if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
                # Frear: reduz velocidade visual
                self.velocidade_kmh = max(20, self.velocidade_kmh - 3)

            self.jogador_x += self.jogador_vel

        # —— Limita jogador à pista ——
        hw = self.jogador_w // 2
        self.jogador_x = max(PISTA_ESQUERDA + hw,
                             min(PISTA_DIREITA - hw, self.jogador_x))

        # —— Timers ——
        if self.invencivel > 0:
            self.invencivel -= 1
        if self.tremor > 0:
            self.tremor -= 1
        if self.turbo_ativo > 0:
            self.turbo_ativo -= 1
        if self.escudo_ativo > 0:
            self.escudo_ativo -= 1

        # —— Pontuação por tempo ——
        if self.tempo_jogo % 10 == 0:
            self.pontos += self.nivel

        # —— Spawn de inimigos ——
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_intervalo:
            self.spawn_timer = 0
            qtd = 1 + (self.nivel // 3)   # mais inimigos em níveis altos
            for _ in range(min(qtd, 3)):
                self.inimigos.append(Inimigo(self.vel_scroll))

        # —— Spawn de power-ups ——
        self.spawn_pu_timer += 1
        if self.spawn_pu_timer >= self.spawn_pu_intervalo:
            self.spawn_pu_timer = 0
            self.powerups.append(PowerUp(self.vel_scroll))

        # —— Update inimigos ——
        for ini in self.inimigos:
            ini.update(scroll_real)
            # Pontos extras ao desviar por pouco (< 80px horizontal)
            if not ini.passou and ini.y > self.jogador_y + self.jogador_h:
                ini.passou = True
                dist_x = abs(ini.x - self.jogador_x)
                if dist_x < 80:
                    self.pontos += 25   # bônus desvio arriscado

        # —— Colisão jogador ↔ inimigo ——
        rect_jog = pygame.Rect(
            self.jogador_x - self.jogador_w // 2 + 6,
            self.jogador_y - self.jogador_h // 2 + 6,
            self.jogador_w - 12, self.jogador_h - 12)

        for ini in self.inimigos[:]:
            if rect_jog.colliderect(ini.rect) and self.invencivel == 0:
                if self.escudo_ativo > 0:
                    # Escudo absorve o golpe
                    self.escudo_ativo = 0
                    self._explosao(ini.x, ini.y, cor=CIANO)
                    self.inimigos.remove(ini)
                else:
                    self.vidas -= 1
                    self.invencivel = 120          # 2 s de invencibilidade
                    self.tremor = 30
                    self.tremor_amp = 8
                    self._explosao(self.jogador_x, self.jogador_y)
                    if self.som_colisao:
                        self.som_colisao.play()
                    self.inimigos.remove(ini)
                    if self.vidas <= 0:
                        if self.som_motor:
                            self.som_motor.stop()
                        self.estado = "GAME_OVER"
                        return

        # —— Colisão jogador ↔ power-up ——
        for pu in self.powerups[:]:
            pu_rect = pygame.Rect(pu.x - pu.raio, int(pu.y) - pu.raio,
                                  pu.raio * 2, pu.raio * 2)
            if rect_jog.colliderect(pu_rect):
                if pu.tipo == "turbo":
                    self.turbo_ativo = 180         # 3 s
                    self.pontos += 50
                else:
                    self.escudo_ativo = 300        # 5 s
                    self.pontos += 30
                self._explosao(pu.x, int(pu.y),
                               cor=AMARELO if pu.tipo == "turbo" else CIANO)
                if self.som_powerup:
                    self.som_powerup.play()
                self.powerups.remove(pu)

        # —— Remove fora de tela ——
        self.inimigos  = [i for i in self.inimigos  if not i.fora]
        self.powerups  = [p for p in self.powerups  if not p.fora]

        # —— Update power-ups ——
        for pu in self.powerups:
            pu.update(scroll_real)

        # —— Update partículas ——
        for p in self.particulas:
            p.update()
        self.particulas = [p for p in self.particulas if not p.morta]

    # ──────────────────────────────────────────
    #  EXPLOSÃO — cria partículas
    # ──────────────────────────────────────────
    def _explosao(self, x, y, cor=None):
        """Cria partículas de explosão centradas em (x, y)."""
        for _ in range(30):
            self.particulas.append(Particula(x, y, cor))

    # ──────────────────────────────────────────
    #  DESENHO — tudo o que aparece na tela
    # ──────────────────────────────────────────
    def _desenhar(self):
        # Tremor de câmera
        tx = random.randint(-self.tremor_amp, self.tremor_amp) if self.tremor > 0 else 0
        ty = random.randint(-self.tremor_amp, self.tremor_amp) if self.tremor > 0 else 0
        if self.tremor > 0:
            self.tremor_amp = max(0, self.tremor_amp - 0.3)

        surf = pygame.Surface((LARGURA, ALTURA))
        self._desenha_fundo(surf)
        self._desenha_pista(surf)
        self._desenha_objetos_fundo(surf)
        self._desenha_powerups(surf)
        self._desenha_inimigos(surf)
        self._desenha_jogador(surf)
        self._desenha_particulas(surf)
        self._desenha_hud(surf)

        # Aplica tremor ao blit final
        self.tela.fill(PRETO)
        self.tela.blit(surf, (tx, ty))

    def _desenha_fundo(self, surf):
        """Preenche as laterais (deserto/areia)."""
        surf.fill(COR_FUNDO)

    def _desenha_objetos_fundo(self, surf):
        """Cactos, arbustos e pedras animados nas laterais."""
        for obj in self.objetos_fundo:
            x, y, t, tam = obj["x"], int(obj["y"]), obj["tipo"], obj["tam"]
            if t == "cacto":
                # Haste central
                pygame.draw.rect(surf, (80, 120, 60),
                                 (x - 3, y - tam, 6, tam), border_radius=2)
                # Braço esquerdo
                pygame.draw.rect(surf, (80, 120, 60),
                                 (x - tam // 2, y - tam // 2, tam // 2, 4))
                pygame.draw.rect(surf, (80, 120, 60),
                                 (x - tam // 2, y - tam // 2 - 8, 4, 8))
                # Braço direito
                pygame.draw.rect(surf, (80, 120, 60),
                                 (x, y - tam // 2, tam // 2, 4))
                pygame.draw.rect(surf, (80, 120, 60),
                                 (x + tam // 2 - 4, y - tam // 2 - 8, 4, 8))
            elif t == "arbusto":
                pygame.draw.circle(surf, (100, 140, 70), (x, y), tam // 2)
                pygame.draw.circle(surf, (120, 160, 80),
                                   (x - tam // 4, y - tam // 4), tam // 3)
            else:  # pedra
                pygame.draw.ellipse(surf, CINZA,
                                    (x - tam // 2, y - tam // 3, tam, tam // 1.5))
                pygame.draw.ellipse(surf, CINZA_CLARO,
                                    (x - tam // 2 + 2, y - tam // 3 + 2,
                                     tam - 4, tam // 2 - 2))

    def _desenha_pista(self, surf):
        """Desenha asfalto, calçadas, marcações e linhas centrais animadas."""
        # Calçadas
        pygame.draw.rect(surf, COR_CALÇADA,
                         (PISTA_ESQUERDA - 18, 0, 18, ALTURA))
        pygame.draw.rect(surf, COR_CALÇADA,
                         (PISTA_DIREITA, 0, 18, ALTURA))

        # Asfalto
        pygame.draw.rect(surf, COR_PISTA,
                         (PISTA_ESQUERDA, 0, PISTA_DIREITA - PISTA_ESQUERDA, ALTURA))

        # Bordas brancas da pista
        pygame.draw.rect(surf, BRANCO,
                         (PISTA_ESQUERDA, 0, 4, ALTURA))
        pygame.draw.rect(surf, BRANCO,
                         (PISTA_DIREITA - 4, 0, 4, ALTURA))

        # Linhas centrais tracejadas (animadas pelo offset)
        for y in range(-60, ALTURA + 60, 60):
            yy = (y + int(self.offset_estrada)) % (ALTURA + 60) - 30
            pygame.draw.rect(surf, AMARELO,
                             (PISTA_CENTRO - 3, yy, 6, 35), border_radius=2)

        # Linha de faixa 1/3 e 2/3 (cinza suave)
        x1 = PISTA_ESQUERDA + (PISTA_DIREITA - PISTA_ESQUERDA) // 3
        x2 = PISTA_ESQUERDA + (PISTA_DIREITA - PISTA_ESQUERDA) * 2 // 3
        for y in range(-60, ALTURA + 60, 60):
            yy = (y + int(self.offset_estrada)) % (ALTURA + 60) - 30
            pygame.draw.rect(surf, CINZA,
                             (x1 - 1, yy, 2, 25), border_radius=1)
            pygame.draw.rect(surf, CINZA,
                             (x2 - 1, yy, 2, 25), border_radius=1)

    def _desenha_powerups(self, surf):
        for pu in self.powerups:
            pu.draw(surf)

    def _desenha_inimigos(self, surf):
        for ini in self.inimigos:
            ini.draw(surf)

    def _desenha_jogador(self, surf):
        """Desenha o carro do jogador; pisca se invencível."""
        if self.invencivel > 0 and (self.invencivel // 6) % 2 == 0:
            return  # efeito de piscar

        jx, jy = int(self.jogador_x), int(self.jogador_y)

        # Escudo visual
        if self.escudo_ativo > 0:
            alpha = 120 + int(math.sin(pygame.time.get_ticks() / 80) * 60)
            s = pygame.Surface((self.jogador_w + 30, self.jogador_h + 30),
                                pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*CIANO, alpha),
                                (0, 0, self.jogador_w + 30, self.jogador_h + 30), 4)
            surf.blit(s, (jx - (self.jogador_w + 30) // 2,
                          jy - (self.jogador_h + 30) // 2))

        # Turbo: rastro de chamas
        if self.turbo_ativo > 0:
            for i in range(5):
                fy = jy + self.jogador_h // 2 + i * 8 + random.randint(-3, 3)
                fx = jx + random.randint(-8, 8)
                r = max(2, 10 - i * 2)
                cor = [AMARELO, LARANJA, VERMELHO][min(i // 2, 2)]
                pygame.draw.circle(surf, cor, (fx, fy), r)

        # Carro azul/branco
        desenha_carro(surf, jx, jy, self.jogador_w, self.jogador_h,
                      AZUL, BRANCO, cor_vidro=(200, 230, 255))

    def _desenha_particulas(self, surf):
        for p in self.particulas:
            p.draw(surf)

    def _desenha_hud(self, surf):
        """HUD: pontos, velocidade, vidas, nível, ícones de turbo/escudo."""
        # Fundo semi-transparente do HUD
        hud = pygame.Surface((LARGURA, 54), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 160))
        surf.blit(hud, (0, 0))

        # Pontuação
        txt = self.fonte_hud.render(f"PTS  {self.pontos:07d}", True, AMARELO)
        surf.blit(txt, (10, 8))

        # Velocidade
        txt_vel = self.fonte_hud.render(f"{self.velocidade_kmh} km/h", True, VERDE_CLARO)
        surf.blit(txt_vel, (LARGURA // 2 - txt_vel.get_width() // 2, 8))

        # Vidas (corações)
        for i in range(3):
            cor = VERMELHO if i < self.vidas else CINZA
            pygame.draw.polygon(surf, cor, self._coração(340 + i * 30, 18, 10))

        # Nível
        txt_nv = self.fonte_pequena.render(f"NÍV {self.nivel}", True, CINZA_CLARO)
        surf.blit(txt_nv, (10, 32))

        # Barra de velocidade
        barra_max = 120
        barra_val = int(barra_max * min(self.velocidade_kmh, 260) / 260)
        pygame.draw.rect(surf, CINZA, (LARGURA // 2 - barra_max // 2, 32, barra_max, 12),
                         border_radius=4)
        cor_bar = VERDE_CLARO if self.velocidade_kmh < 180 else \
                  (AMARELO if self.velocidade_kmh < 230 else VERMELHO)
        pygame.draw.rect(surf, cor_bar,
                         (LARGURA // 2 - barra_max // 2, 32, barra_val, 12),
                         border_radius=4)

        # Ícone turbo ativo
        if self.turbo_ativo > 0:
            t = self.fonte_pequena.render(
                f"⚡ TURBO  {self.turbo_ativo // 60 + 1}s", True, AMARELO)
            surf.blit(t, (10, ALTURA - 30))

        # Ícone escudo ativo
        if self.escudo_ativo > 0:
            s = self.fonte_pequena.render(
                f"🛡 ESCUDO {self.escudo_ativo // 60 + 1}s", True, CIANO)
            surf.blit(s, (10, ALTURA - 52))

    def _coração(self, cx, cy, r):
        """Retorna pontos de um coração simples."""
        pts = []
        for ang in range(0, 360, 5):
            a = math.radians(ang)
            x = r * (16 * math.sin(a) ** 3) / 16
            y = -r * (13 * math.cos(a) - 5 * math.cos(2*a) -
                      2 * math.cos(3*a) - math.cos(4*a)) / 16
            pts.append((cx + x, cy + y))
        return pts

    # ──────────────────────────────────────────
    #  TELA INICIAL
    # ──────────────────────────────────────────
    def _tela_inicio(self):
        self.tela.fill(CINZA_ESCURO)

        # Estrada decorativa ao fundo
        pygame.draw.rect(self.tela, COR_PISTA,
                         (PISTA_ESQUERDA, 0, PISTA_DIREITA - PISTA_ESQUERDA, ALTURA))

        # Título com sombra
        titulo = self.fonte_titulo.render("TURBO", True, AMARELO)
        titulo2 = self.fonte_titulo.render("RACER", True, VERMELHO)
        cx = LARGURA // 2
        self.tela.blit(titulo, (cx - titulo.get_width() // 2 + 3, 123))
        self.tela.blit(titulo2, (cx - titulo2.get_width() // 2 + 3, 183))
        self.tela.blit(titulo, (cx - titulo.get_width() // 2, 120))
        self.tela.blit(titulo2, (cx - titulo2.get_width() // 2, 180))

        # Subtítulo pulsante
        pulse = abs(math.sin(pygame.time.get_ticks() / 500))
        cor_pulse = (int(200 + 55 * pulse), int(200 + 55 * pulse), 255)
        sub = self.fonte_media.render("Pressione qualquer tecla para começar", True, cor_pulse)
        self.tela.blit(sub, (cx - sub.get_width() // 2, 320))

        # Controles
        ctrl = [
            "A / ← → Esquerda",
            "D / → → Direita",
            "Mouse → Arrastar carro",
            "Colete ⚡ Turbo e 🛡 Escudo!",
        ]
        for i, c in enumerate(ctrl):
            t = self.fonte_pequena.render(c, True, CINZA_CLARO)
            self.tela.blit(t, (cx - t.get_width() // 2, 400 + i * 24))

        # Carro decorativo
        desenha_carro(self.tela, cx, 550, 50, 80, AZUL, BRANCO)

    # ──────────────────────────────────────────
    #  TELA GAME OVER
    # ──────────────────────────────────────────
    def _tela_game_over(self):
        self.tela.fill(CINZA_ESCURO)

        # Overlay vermelho pulsante
        alpha = int(60 + 30 * abs(math.sin(pygame.time.get_ticks() / 400)))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((200, 20, 20, alpha))
        self.tela.blit(overlay, (0, 0))

        cx = LARGURA // 2

        # Título
        go = self.fonte_titulo.render("GAME OVER", True, VERMELHO)
        self.tela.blit(go, (cx - go.get_width() // 2, 180))

        # Pontuação final
        pts = self.fonte_grande.render(f"Pontos: {self.pontos}", True, AMARELO)
        self.tela.blit(pts, (cx - pts.get_width() // 2, 280))

        nv = self.fonte_media.render(f"Nível alcançado: {self.nivel}", True, BRANCO)
        self.tela.blit(nv, (cx - nv.get_width() // 2, 330))

        # Piscando
        pulse = abs(math.sin(pygame.time.get_ticks() / 500))
        cor_r = (int(200 + 55 * pulse), 255, int(200 + 55 * pulse))
        r = self.fonte_media.render("[ R ]  Jogar novamente", True, cor_r)
        self.tela.blit(r, (cx - r.get_width() // 2, 420))

        esc = self.fonte_pequena.render("ESC  →  Sair", True, CINZA_CLARO)
        self.tela.blit(esc, (cx - esc.get_width() // 2, 460))


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    jogo = JogoCorrida()
    jogo.run()
