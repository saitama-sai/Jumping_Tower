import pygame
import random

pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Jumpy Tower')
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
bg_image = pygame.image.load('assets/bg.png').convert_alpha()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)


class Player(pygame.sprite.Sprite):
    def __init__(self, blocks):
        super().__init__()

        # === Animasyon çerçevelerini tutacak sözlük ===
        self.frames = {
            "idle": [],
            "run": [],
            "jump": [],
            "fall": [],
            "hit": [],
            "flip": []
        }

        # === Animasyonları yükle ===
        self.load_run_frames()
        self.load_jump_frames()
        self.load_idle_frames()
        self.load_hit_frames()
        self.load_flip_frames()

        # === Başlangıç animasyonu ve görüntüsü ===
        self.current_action = "idle"
        self.frame_index = 0
        self.image = self.frames["idle"][0] if self.frames["idle"] else pygame.Surface((64, 64))
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, blocks[0].rect.top + 1))

        # === Kamera ayarları ===
        self.camera_y = self.rect.y
        self.camera_offset = 250
        self.camera_speed_up = 0.15
        self.camera_speed_down = 0.05

        # === Fiziksel hareket değişkenleri ===
        self.vel_y = 0
        self.vel_x = 0
        self.gravity_boost = 0
        self.wall_bounce = False
        self.movement_slowdown = 1.0

        # === Zıplama ile ilgili değişkenler ===
        self.can_jump = True
        self.is_jumping = False
        self.jump_pressed = False
        self.power = 0
        self.max_power = 90
        self.power_increase = 25
        self.power_decrease = 0.1
        self.jump_count = 0
        self.last_jumped_block = None

        # === Flip (takla) hareketi ===
        self.flipping = False
        self.flip_timer = 0
        self.flip_duration = 20
        self.flip_jump_boost = -20
        self.consecutive_flips = 0
        self.flip_combo = 1.0

        # === Animasyon zamanlayıcısı ===
        self.anim_timer = 0
        self.anim_speed = 5
        self.facing_right = True

        # === Skor bilgileri ===
        self.score = 0
        self.height_score = 0
        self.max_height = 0
        self.blocks_jumped = 0

        # === Diğer bayraklar ===
        self.is_hit = False
        self.start_scroll = False

    # === KOŞMA animasyon karelerini yükle ===
    def load_run_frames(self):
        for i in range(1, 7):
            try:
                img = pygame.image.load(f"assets/running_frame1-{i}.png").convert_alpha()
                self.frames["run"].append(pygame.transform.scale(img, (64, 64)))
            except Exception as e:
                print(f"running_frame1-{i}.png yüklenemedi:", e)

    # === Zıplama ve düşme animasyonlarını yükle ===
    def load_jump_frames(self):
        try:
            jump_img = pygame.image.load("assets/jump_up1.png").convert_alpha()
            self.frames["jump"].append(pygame.transform.scale(jump_img, (64, 64)))
        except Exception as e:
            print("jump_up1.png yüklenemedi:", e)

        try:
            fall_img = pygame.image.load("assets/jump_fall1.png").convert_alpha()
            self.frames["fall"].append(pygame.transform.scale(fall_img, (64, 64)))
        except Exception as e:
            print("jump_fall1.png yüklenemedi:", e)

    # === Boşta durma (idle) animasyonunu yükle ===
    def load_idle_frames(self):
        try:
            idle1 = pygame.image.load("assets/standing_frame1-1.png").convert_alpha()
            self.frames["idle"].append(pygame.transform.scale(idle1, (64, 64)))
            idle2 = pygame.image.load("assets/standing_frame1-2.png").convert_alpha()
            self.frames["idle"].append(pygame.transform.scale(idle2, (64, 64)))
        except Exception as e:
            print("Idle frame yüklenemedi:", e)

    # === Hasar yeme (hit) animasyonunu yükle ===
    def load_hit_frames(self):
        try:
            hit_img = pygame.image.load("assets/frame-got-hit1.png").convert_alpha()
            self.frames["hit"].append(pygame.transform.scale(hit_img, (64, 64)))
        except Exception as e:
            print("frame-got-hit1.png yüklenemedi:", e)

    # === Flip (takla) animasyonunu yükle veya oluştur ===
    def load_flip_frames(self):
        try:
            flip_img = pygame.image.load("assets/flip.png").convert_alpha()
            for i in range(4):
                rotated = pygame.transform.rotate(flip_img, i * 90)
                scaled = pygame.transform.scale(rotated, (64, 64))
                self.frames["flip"].append(scaled)
        except Exception as e:
            print("flip.png yüklenemedi:", e)

            # Eğer flip.png yoksa jump görselinden döndürerek flip animasyonu oluştur
            if self.frames["jump"] and len(self.frames["jump"]) > 0:
                for i in range(4):
                    flip_img = pygame.transform.rotate(self.frames["jump"][0], i * 90)
                    self.frames["flip"].append(flip_img)
            else:
                # Hiçbir şey yüklenemezse mavi kutu ile geçici görüntü oluştur
                dummy = pygame.Surface((64, 64))
                dummy.fill(BLUE)
                self.frames["flip"].append(dummy)

