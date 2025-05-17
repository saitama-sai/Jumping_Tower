import pygame
import random
import os

# Pygame başlatılıyor
pygame.init()

# Ekran boyutları tanımlanıyor
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Jumpy Tower')  # Oyun başlığı ayarlanıyor

# Renk tanımlamaları
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Arkaplan resmi yükleniyor, hata durumunda düz renk kullanılıyor
try:
    bg_image = pygame.image.load('assets/bg.png').convert_alpha()
except:
    bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_image.fill((50, 50, 80))

# Yazı fontları tanımlanıyor
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Oyun hızı tanımlanıyor
game_speed = 1.5


# Oyuncu sınıfı tanımlanıyor
class Player(pygame.sprite.Sprite):
    def __init__(self, blocks):
        super().__init__()
        # Animasyon kareleri için boş listeler oluşturuluyor
        self.frames = {"idle": [], "run": [], "jump": [], "fall": [], "hit": [], "flip": []}
        self._load_frames()  # Animasyon kareleri yükleniyor
        self.current_action = "idle"  # Başlangıç durumu "idle" olarak ayarlanıyor
        self.frame_index = 0  # Animasyon kare indeksi
        # İlk görsel ayarlanıyor, eğer "idle" animasyonu yoksa boş bir Surface oluşturuluyor
        self.image = self.frames["idle"][0] if self.frames["idle"] else pygame.Surface((64, 64))
        # Karakterin konum bilgisi, ilk blok üzerinde başlatılıyor
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, blocks[0].rect.top + 1))

        # Başlangıç değerleri için yardımcı fonksiyonlar çağrılıyor
        self._init_physics()  # Fizik değişkenleri
        self._init_animation()  # Animasyon değişkenleri
        self._init_gameplay_vars()  # Oynanış değişkenleri
        self._init_score_vars()  # Skor değişkenleri

    # Animasyon karelerini yükleyen fonksiyon
    def _load_frames(self):
        # Koşma animasyonu için 6 kare yükleniyor
        for i in range(1, 7):
            try:
                img = pygame.image.load(f"assets/running_frame1-{i}.png").convert_alpha()
                self.frames["run"].append(pygame.transform.scale(img, (64, 64)))
            except Exception as e:
                print(f"Couldn't load running_frame1-{i}.png:", e)
        self._load_specific_frames()  # Diğer özel animasyon kareleri yükleniyor

    # Özel animasyon karelerini yükleyen fonksiyon
    def _load_specific_frames(self):
        # Her durum için dosya yolları tanımlanıyor
        frame_paths = {
            "jump": ["assets/jump_up1.png"],  # Zıplama karesi
            "fall": ["assets/jump_fall1.png"],  # Düşme karesi
            "hit": ["assets/frame-got-hit1.png"],  # Hasar alma karesi
            "idle": ["assets/standing_frame1-1.png", "assets/standing_frame1-2.png"]  # Durma kareleri
        }

        # Her durum için ilgili resimleri yükleme
        for action, paths in frame_paths.items():
            for path in paths:
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.frames[action].append(pygame.transform.scale(img, (64, 64)))
                except Exception as e:
                    print(f"Couldn't load {path}:", e)

        self._load_flip_frames()  # Takla animasyonu yükleniyor

    # Takla animasyonu için kareleri yükleyen fonksiyon
    def _load_flip_frames(self):
        try:
            flip_img = pygame.image.load("assets/flip.png").convert_alpha()
            # 4 farklı açıda döndürülmüş takla karesi oluşturuluyor
            for i in range(4):
                rotated = pygame.transform.rotate(flip_img, i * 90)
                scaled = pygame.transform.scale(rotated, (64, 64))
                self.frames["flip"].append(scaled)
        except Exception as e:
            print("Couldn't load flip.png:", e)
            # Hata durumunda alternatif olarak zıplama karesi kullanılıyor
            if self.frames["jump"] and len(self.frames["jump"]) > 0:
                for i in range(4):
                    flip_img = pygame.transform.rotate(self.frames["jump"][0], i * 90)
                    self.frames["flip"].append(flip_img)
            else:
                # Hiçbir görsel yoksa mavi bir kare kullanılıyor
                dummy = pygame.Surface((64, 64))
                dummy.fill(BLUE)
                self.frames["flip"].append(dummy)

    # Fizik değişkenlerini başlatan fonksiyon
    def _init_physics(self):
        self.camera_y = self.rect.y  # Kamera y pozisyonu
        self.camera_offset = 250  # Kamera ofset değeri
        self.camera_speed_up = 0.15  # Kamera yukarı hareket hızı
        self.camera_speed_down = 0.05  # Kamera aşağı hareket hızı
        self.vel_y = 0  # Dikey hız
        self.vel_x = 0  # Yatay hız
        self.gravity_boost = 0  # Yerçekimi artışı
        self.movement_slowdown = 1.0  # Hareket yavaşlatma faktörü

    # Animasyon değişkenlerini başlatan fonksiyon
    def _init_animation(self):
        self.anim_timer = 0  # Animasyon zamanlayıcısı
        self.anim_speed = 5  # Animasyon hızı
        self.is_hit = False  # Hasar alınıp alınmadığı
        self.facing_right = True  # Karakterin sağa bakıp bakmadığı

    # Oynanış değişkenlerini başlatan fonksiyon
    def _init_gameplay_vars(self):
        self.start_scroll = False  # Kaydırma başladı mı
        self.can_jump = True  # Zıplayabilir mi
        self.is_jumping = False  # Zıplıyor mu
        self.jump_pressed = False  # Zıplama tuşuna basıldı mı
        self.power = 0  # Güç miktarı
        self.max_power = 90  # Maksimum güç
        self.power_increase = 25  # Güç artış miktarı
        self.power_decrease = 0.1  # Güç azalma miktarı
        self.flipping = False  # Takla atılıyor mu
        self.flip_timer = 0  # Takla zamanlayıcısı
        self.flip_duration = 20  # Takla süresi
        self.flip_jump_boost = -20  # Takla zıplama artışı
        self.blocks_jumped = 0  # Zıplanan blok sayısı
        self.consecutive_flips = 0  # Ardışık takla sayısı
        self.flip_combo = 1.0  # Takla çarpanı
        self.wall_bounce = False  # Duvardan sekme
        self.last_jumped_block = None  # Son zıplanan blok
        self.jump_count = 0  # Zıplama sayısı

    # Skor değişkenlerini başlatan fonksiyon
    def _init_score_vars(self):
        self.score = 0  # Toplam skor
        self.height_score = 0  # Yükseklik skoru
        self.max_height = 0  # Maksimum yükseklik

    # Her karede çağrılan güncelleme fonksiyonu
    def update(self, keys, blocks):
        dx = 0  # X-ekseni hareket miktarı
        dy = 0  # Y-ekseni hareket miktarı
        moving = False  # Hareket ediliyor mu

        self._update_power()  # Güç miktarı güncelleniyor

        # Duruma göre hareket işlemleri
        if self.flipping:
            dx = self._handle_flipping(keys, blocks)  # Takla durumunda hareket
        elif not self.is_hit:
            dx, moving = self._handle_normal_movement(keys, blocks)  # Normal hareket
            self._handle_jumping(keys, blocks)  # Zıplama kontrolü
            dy = self._apply_gravity()  # Yerçekimi uygulanıyor
            self._handle_screen_boundaries(dx)  # Ekran sınırları kontrolü

        # Konum güncelleniyor
        self.rect.x += dx
        self.rect.y += dy

        self._check_collision(blocks)  # Çarpışma kontrolü
        self._update_animation_state(moving)  # Animasyon durumu güncelleniyor
        self._check_block_landing(blocks)  # Blok üzerine inme kontrolü
        self._animate()  # Animasyon güncelleniyor
        self._update_score()  # Skor güncelleniyor

    # Güç miktarını güncelleyen fonksiyon
    def _update_power(self):
        if self.power > 0 and not self.flipping:
            self.power -= self.power_decrease
            if self.power < 0:
                self.power = 0

    # Takla durumunda hareketi yöneten fonksiyon
    def _handle_flipping(self, keys, blocks):
        self.flip_timer += 1
        self._check_wall_collision()  # Duvar çarpışması kontrolü
        dx = self.vel_x

        # Takla süresi doldu mu
        if self.flip_timer >= self.flip_duration:
            self._end_flip()  # Takla sonlandırılıyor
            return 0
        else:
            self.vel_y = self.flip_jump_boost
            # Takla sırasında sağ sol hareket kontrolü
            if keys[pygame.K_LEFT]:
                self.vel_x -= 0.5
                self.facing_right = False
            if keys[pygame.K_RIGHT]:
                self.vel_x += 0.5
                self.facing_right = True

            self._clamp_velocity()  # Hız sınırlandırılıyor
            return self.vel_x

    # Duvar çarpışmasını kontrol eden fonksiyon
    def _check_wall_collision(self):
        if self.rect.left <= 0:
            self._handle_wall_bounce(True)  # Sol duvardan sekme
        elif self.rect.right >= SCREEN_WIDTH:
            self._handle_wall_bounce(False)  # Sağ duvardan sekme

    # Duvardan sekme işlemini yöneten fonksiyon
    def _handle_wall_bounce(self, from_left):
        # Sekme yönüne göre hız değişimi
        self.vel_x = abs(self.vel_x) * 1.2 if from_left else -abs(self.vel_x) * 1.2
        self.facing_right = True if from_left else False
        self.consecutive_flips += 1  # Ardışık takla sayısı artırılıyor
        self.flip_combo += 0.5  # Takla çarpanı artırılıyor
        self.wall_bounce = True  # Duvardan sekme aktif
        self.power += 5  # Güç artırılıyor
        self.flip_duration += 10  # Takla süresi uzatılıyor
        self.score += int(10 * self.flip_combo)  # Skor artırılıyor

    # Takla sonlandırma fonksiyonu
    def _end_flip(self):
        self.flipping = False
        self.flip_timer = 0
        self.vel_y = 2
        self.vel_x = 0

        # Duvardan sekme olmadıysa çarpan sıfırlanıyor
        if not self.wall_bounce:
            self.flip_combo = 1
        else:
            # Duvardan sekme sonrası fiziksel etkiler
            self.gravity_boost = 0.4
            self.movement_slowdown = 0.7

        self.wall_bounce = False

    # Hızı sınırlandıran fonksiyon
    def _clamp_velocity(self):
        if self.vel_x > 12:
            self.vel_x = 12
        if self.vel_x < -12:
            self.vel_x = -12

    # Normal hareketi yöneten fonksiyon
    def _handle_normal_movement(self, keys, blocks):
        move_speed = 5  # Hareket hızı

        # Yavaşlatma faktörü varsa hareket hızı azaltılıyor
        if hasattr(self, 'movement_slowdown') and self.movement_slowdown < 1.0:
            move_speed *= self.movement_slowdown
            self.movement_slowdown += 0.01
            if self.movement_slowdown > 1.0:
                self.movement_slowdown = 1.0

        dx = 0
        moving = False

        # Sol tuş kontrolü
        if keys[pygame.K_LEFT]:
            dx = -move_speed
            self.facing_right = False
            moving = True

        # Sağ tuş kontrolü
        if keys[pygame.K_RIGHT]:
            dx = move_speed
            self.facing_right = True
            moving = True

        return dx, moving

    # Zıplama işlemini yöneten fonksiyon
    def _handle_jumping(self, keys, blocks):
        on_ground = self._on_ground(blocks)  # Zemin üzerinde mi kontrolü

        if on_ground:
            self._handle_landing()  # İnme işlemi

        # Zıplama ve takla tuşları kontrolü
        jump_key_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP]
        flip_key_pressed = keys[pygame.K_f]

        # Zıplama koşulları sağlanıyorsa zıplama yapılıyor
        if jump_key_pressed and not self.jump_pressed and on_ground:
            self._perform_jump()

        # Güç yeterliyse takla atılıyor
        if flip_key_pressed and self.power >= self.max_power * 0.9:
            self._start_flipping()

        self.jump_pressed = jump_key_pressed

    # İnme durumunu yöneten fonksiyon
    def _handle_landing(self):
        self.is_jumping = False

        # İnme sonrası takla çarpanı sıfırlanıyor
        if self.flip_combo > 1:
            self.flip_combo = 1

        # Yerçekimi artışı varsa sıfırlanıyor
        if hasattr(self, 'gravity_boost') and self.gravity_boost > 0:
            self.gravity_boost = 0

    # Zıplama işlemini gerçekleştiren fonksiyon
    def _perform_jump(self):
        self.vel_y = -11  # Dikey hız ayarlanıyor (yukarı doğru)
        self.is_jumping = True
        self.start_scroll = True

        # Güç artırılıyor
        self.power += self.power_increase
        if self.power > self.max_power:
            self.power = self.max_power

        self.last_jumped_block = None  # Son zıplanan blok sıfırlanıyor
        self.jump_count += 1  # Zıplama sayısı artırılıyor
        self.score += 5  # Skor artırılıyor

    # Yerçekimini uygulayan fonksiyon
    def _apply_gravity(self):
        gravity = 0.6  # Temel yerçekimi değeri

        # Yerçekimi artışı varsa ekleniyor
        if hasattr(self, 'gravity_boost') and self.gravity_boost > 0:
            gravity += self.gravity_boost
            self.gravity_boost -= 0.01
            if self.gravity_boost < 0:
                self.gravity_boost = 0

        # Dikey hız güncelleniyor (düşme etkisi)
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y = 10

        return self.vel_y

    # Ekran sınırlarını kontrol eden fonksiyon
    def _handle_screen_boundaries(self, dx):
        # Sol sınır kontrolü
        if self.rect.left + dx < 0:
            dx = -self.rect.left

        # Sağ sınır kontrolü
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

    # Animasyon durumunu güncelleyen fonksiyon
    def _update_animation_state(self, moving):
        if self.flipping:
            self.current_action = "flip"  # Takla animasyonu
        elif not self.is_hit:
            if self.vel_y < 0:
                self.current_action = "jump"  # Zıplama animasyonu
            elif self.vel_y > 4:
                self.current_action = "fall"  # Düşme animasyonu
            elif moving:
                self.current_action = "run"  # Koşma animasyonu
            else:
                self.current_action = "idle"  # Durma animasyonu
        else:
            self.current_action = "hit"  # Hasar alma animasyonu

    # Blok üzerine inmeyi kontrol eden fonksiyon
    def _check_block_landing(self, blocks):
        for block in blocks:
            # Karakter blok üzerine iniyor mu kontrolü
            if self.rect.bottom <= block.rect.top and self.rect.bottom + self.vel_y >= block.rect.top:
                if self.rect.right > block.rect.left and self.rect.left < block.rect.right:
                    # Takla durumunda skor artışı
                    if self.flipping:
                        self.blocks_jumped += 1
                        self.score += int(5 * self.flip_combo)
                        self.power -= 5
                        if self.power < 0:
                            self.power = 0
                    # Normal durumda skor artışı (her blok için bir kez)
                    elif block != self.last_jumped_block:
                        self.score += 3
                        self.last_jumped_block = block

    # Skoru güncelleyen fonksiyon
    def _update_score(self):
        current_height = -self.rect.y  # Mevcut yükseklik

        # Yeni maksimum yüksekliğe ulaşılmışsa
        if current_height > self.max_height:
            height_diff = current_height - self.max_height
            self.max_height = current_height

            # Her 130 birimlik yükselme için skor artışı
            floors_passed = int(height_diff / 130)
            if floors_passed > 0:
                self.height_score += floors_passed * 50
                self.score += floors_passed * 50

    # Takla atmayı başlatan fonksiyon
    def _start_flipping(self):
        self.flipping = True
        self.flip_timer = 0
        self.vel_y = self.flip_jump_boost  # Dikey hız ayarlanıyor

        # Yatay hız, karakterin bakış yönüne göre ayarlanıyor
        if self.facing_right:
            self.vel_x = 6
        else:
            self.vel_x = -6

        self.power *= 0.7  # Güç azaltılıyor
        self.consecutive_flips = 0  # Ardışık takla sayısı sıfırlanıyor
        self.wall_bounce = False  # Duvar sekmesi sıfırlanıyor

    # Animasyonu güncelleyen fonksiyon
    def _animate(self):
        # İlgili animasyon kareleri var mı kontrolü
        if self.frames.get(self.current_action) and len(self.frames[self.current_action]) > 0:
            self.anim_timer += 1

            # Animasyon zamanı geldiyse kare değiştiriliyor
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index += 1

                # Son kareye gelindiğinde başa sarılıyor (hasar hariç)
                if self.frame_index >= len(self.frames[self.current_action]):
                    if self.current_action != "hit":
                        self.frame_index = 0
                    else:
                        self.frame_index = len(self.frames[self.current_action]) - 1

            # Güncel kare kullanılıyor
            if self.frame_index < len(self.frames[self.current_action]):
                self.image = self.frames[self.current_action][self.frame_index]
            else:
                self.frame_index = 0
                self.image = self.frames[self.current_action][self.frame_index]
        else:
            # Animasyon bulunamazsa kırmızı bir kare kullanılıyor
            self.image = pygame.Surface((64, 64))
            self.image.fill((255, 0, 0))

    # Zemin üzerinde olup olmadığını kontrol eden fonksiyon
    def _on_ground(self, blocks):
        for block in blocks:
            # Karakter bloğun üzerinde mi kontrolü
            if self.rect.bottom <= block.rect.top + 5 and self.rect.bottom >= block.rect.top - 10:
                if self.rect.right > block.rect.left and self.rect.left < block.rect.right:
                    return True
        return False

    # Çarpışmaları kontrol eden fonksiyon
    def _check_collision(self, blocks):
        # Takla durumunda çarpışma kontrolü yapılmıyor
        if self.flipping:
            return

        for block in blocks:
            if self.rect.colliderect(block.rect):
                # Düşerken blok üzerine çarpma
                if self.vel_y > 0 and self.rect.bottom <= block.rect.bottom:
                    self.rect.bottom = block.rect.top + 1
                    self.vel_y = 0

    # Karakteri ekrana çizen fonksiyon
    def draw(self, surface):
        # Karakterin bakış yönüne göre görsel çevriliyor
        flipped_image = pygame.transform.flip(self.image, not self.facing_right, False)

        # Takla durumunda özel efektler
        if self.flipping:
            if self.wall_bounce:
                # Duvardan sekmede büyütülmüş görsel
                scaled_image = pygame.transform.scale(flipped_image,
                                                      (int(flipped_image.get_width() * 1.5),
                                                       int(flipped_image.get_height() * 1.5)))
                surface.blit(scaled_image, (self.rect.centerx - scaled_image.get_width() // 2,
                                            self.rect.centery - scaled_image.get_height() // 2))
            else:
                surface.blit(flipped_image, self.rect)

            # Takla durumunda hareket efekti (hayalet görüntü)
            ghost_img = flipped_image.copy()
            ghost_img.set_alpha(100)
            offset = -10 if self.facing_right else 10
            surface.blit(ghost_img, (self.rect.x - offset, self.rect.y))
        else:
            # Normal durumda karakter çizimi
            surface.blit(flipped_image, self.rect)

        # Kullanıcı arayüzü çiziliyor
        self._draw_ui(surface)

    # Kullanıcı arayüzünü çizen fonksiyon
    def _draw_ui(self, surface):
        info_font = pygame.font.Font(None, 22)
        right_margin = SCREEN_WIDTH - 120

        # Oyun hızı bilgisi
        speed_text = info_font.render(f"Hız: {game_speed:.1f}x", True, WHITE)
        surface.blit(speed_text, (right_margin, 10))

        # Skor bilgisi
        score_text = info_font.render(f"Skor: {self.score}", True, WHITE)
        surface.blit(score_text, (right_margin, 25))

        # Güç çubuğu parametreleri
        power_bar_width = 80
        power_bar_height = 8
        power_bar_x = right_margin
        power_bar_y = 60

        # Güç çubuğu arkaplanı
        pygame.draw.rect(surface, RED, (power_bar_x, power_bar_y, power_bar_width, power_bar_height))

        # Güç çubuğu doluluk oranı
        filled_width = int((self.power / self.max_power) * power_bar_width)

        # Güç yeterliyse renk değişimi (yanıp sönme efekti)
        if self.power >= self.max_power * 0.9:
            bar_color = (0, 255, 255)
            if pygame.time.get_ticks() % 500 < 250:
                bar_color = (255, 255, 0)
        else:
            bar_color = GREEN

        # Güç çubuğu çizimi
        pygame.draw.rect(surface, bar_color, (power_bar_x, power_bar_y, filled_width, power_bar_height))
        pygame.draw.rect(surface, WHITE, (power_bar_x, power_bar_y, power_bar_width, power_bar_height), 1)

        # Güç bilgisi yazısı
        power_text = info_font.render(f"Power: {int(self.power)}/{self.max_power}", True, WHITE)
        surface.blit(power_text, (power_bar_x, power_bar_y - 18))

        # Takla çarpanı bilgisi
        if self.flip_combo > 1:
            combo_text = info_font.render(f"Combo: x{self.flip_combo:.1f}", True, YELLOW)
            surface.blit(combo_text, (power_bar_x, power_bar_y + 15))

        # Zıplanan blok sayısı bilgisi
        if self.flipping or self.blocks_jumped > 0:
            blocks_text = info_font.render(f"Bloklar: {self.blocks_jumped}", True, BLUE)
            surface.blit(blocks_text, (power_bar_x, power_bar_y + 35))


class Block(pygame.sprite.Sprite):
    """
    Block sınıfı - Oyuncunun üzerinde zıplayacağı platformları temsil eder.
    Pygame'in Sprite sınıfından türetilmiştir.
    """

    def __init__(self, x, y, width=150):
        """
        Blok nesnesini başlatır.

        Parametreler:
        - x: Bloğun ekrandaki x koordinatı (merkez noktası)
        - y: Bloğun ekrandaki y koordinatı (üst noktası)
        - width: Bloğun genişliği (varsayılan: 150 piksel)
        """
        super().__init__()  # Sprite sınıfının başlatıcısını çağırır
        try:
            # Blok görselini yüklemeye çalışır
            self.image = pygame.image.load("assets/block.png").convert_alpha()
        except:
            # Görsel yüklenemezse basit bir yeşil dikdörtgen oluşturur
            self.image = pygame.Surface((width, 30))
            self.image.fill((0, 255, 0))  # Yeşil renk (RGB: 0, 255, 0)

        # Görseli istenen boyutlara ölçeklendirir
        self.image = pygame.transform.scale(self.image, (width, 30))

        # Bloğun çarpışma alanını (rect) ayarlar
        self.rect = self.image.get_rect(midtop=(x, y))

    def update(self, scroll, blocks):
        """
        Bloğu günceller ve ekrandan çıktığında yeniden konumlandırır.

        Parametreler:
        - scroll: Kamera kaydırma miktarı (piksel)
        - blocks: Oyundaki tüm blokların listesi (yeniden konumlandırma için gerekli)
        """
        # Bloğu kaydırma miktarı kadar aşağı kaydırır
        self.rect.y += scroll

        # Eğer blok ekranın altından çıkarsa, yeniden konumlandır
        if self.rect.top > SCREEN_HEIGHT:
            self._reset_position(blocks)

    def _reset_position(self, blocks):
        """
        Ekrandan çıkan bloğu yeniden konumlandırır.
        En yüksekteki bloğun üzerine rastgele bir konumda yerleştirir.

        Parametreler:
        - blocks: Oyundaki tüm blokların listesi
        """
        highest_block = None
        highest_y = float('inf')  # Sonsuz değer ile başlatır

        # En yüksekteki bloğu bul
        for block in blocks:
            if block != self and block.rect.y < highest_y:
                highest_y = block.rect.y
                highest_block = block

        if highest_block:
            # Bloğu en yüksekteki bloğun üzerine yerleştir (130 piksel yukarıda)
            self.rect.y = highest_y - 130

            # X koordinatında rastgele bir kayma uygular (sağa veya sola)
            if random.choice([True, False]):
                x_shift = random.randint(50, 150)  # Sağa kayma
            else:
                x_shift = random.randint(-150, -50)  # Sola kayma

            # Yeni x pozisyonunu hesaplar
            new_x = highest_block.rect.centerx + x_shift

            # Ekran sınırlarını aşmayacak şekilde pozisyonu ayarlar
            self.rect.centerx = max(self.rect.width // 2 + 20,
                                    min(new_x, SCREEN_WIDTH - self.rect.width // 2 - 20))

            # Rastgele yeni genişlik belirler (180-250 piksel arası)
            new_width = random.randint(180, 250)

            # Bloğun boyutunu günceller
            self.image = pygame.transform.scale(self.image, (new_width, 30))
            self.rect.width = new_width

    def draw(self, surface):
        """
        Bloğu belirtilen yüzeye çizer.

        Parametreler:
        - surface: Bloğun çizileceği pygame yüzeyi
        """
        surface.blit(self.image, self.rect)


class GameManager:
    """
    GameManager sınıfı - Oyun mantığını ve akışını yönetir.
    Menüler, yüksek skor, oyun döngüsü gibi temel işlevleri kontrol eder.
    """

    def __init__(self):
        """
        Oyun yöneticisini başlatır ve temel değişkenleri ayarlar.
        """
        self.high_score = self._load_high_score()  # Yüksek skoru yükle
        self.in_menu = True  # Oyun başlangıçta menüde
        self.in_help = False  # Yardım ekranında değil
        self.game_active = False  # Oyun aktif değil
        self.blocks = []  # Bloklar listesi
        self.player = None  # Oyuncu nesnesi

    def _load_high_score(self):
        """
        Dosyadan yüksek skoru yükler. Dosya bulunamazsa 0 döndürür.
        """
        try:
            with open("highscore.txt", "r") as file:
                return int(file.read())
        except:
            return 0

    def _save_high_score(self, score):
        """
        Yüksek skoru dosyaya kaydeder.

        Parametreler:
        - score: Kaydedilecek yüksek skor
        """
        try:
            with open("highscore.txt", "w") as file:
                file.write(str(score))
        except:
            pass  # Kaydetme başarısız olursa sessizce devam et

    def create_blocks(self):
        """
        Oyun başlangıcında blokları oluşturur.
        Zemin bloğu ve yukarı doğru uzanan platformları içerir.
        """
        blocks = []

        # Zemin bloğunu oluştur (ekranın en altında, tam genişlikte)
        ground_block = Block(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, SCREEN_WIDTH)
        blocks.append(ground_block)

        # Diğer blokları yukarı doğru oluştur
        y = SCREEN_HEIGHT - 150  # Başlangıç y pozisyonu
        horizontal_variation = 150  # Yatay varyasyon miktarı
        vertical_gap = 130  # Bloklar arası dikey mesafe
        prev_x = SCREEN_WIDTH // 2  # İlk bloğun x pozisyonu

        # 20 blok oluştur
        for i in range(20):
            # Rastgele genişlik belirle (180-250 piksel arası)
            width = random.randint(180, 250)

            # X pozisyonunda rastgele kayma uygula
            if i % 2 == 0:
                x_shift = random.randint(50, horizontal_variation)  # Sağa
            else:
                x_shift = random.randint(-horizontal_variation, -50)  # Sola

            x = prev_x + x_shift

            # Ekran sınırlarını aşmayacak şekilde x pozisyonunu ayarla
            x = max(width // 2 + 20, min(x, SCREEN_WIDTH - width // 2 - 20))

            # Bloğu oluştur ve listeye ekle
            block = Block(x, y, width)
            blocks.append(block)

            # Bir sonraki blok için y pozisyonunu güncelle
            y -= vertical_gap
            prev_x = x

        return blocks

    def draw_help_menu(self):
        """
        Yardım menüsünü ekrana çizer.
        Oyun kontrolleri ve nasıl oynanacağı hakkında bilgiler içerir.
        """
        # Arka planı çiz
        screen.blit(bg_image, (0, 0))

        # Başlığı çiz
        title_font = pygame.font.Font(None, 60)
        title_text = title_font.render("OYNANIS", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)

        # Oyun talimatlarını çiz
        instructions = [
            "Tuşlar: Ok tuşları/SPACE ile zıpla",
            "Power %90 dolunca F ile takla at!",
            "Taklada duvarlardan sekerek COMBO yap!",
            "Yükseldikçe ve blok atladıkça puan kazan",
            "Daha hızlı zıpla, daha yükseğe çık",
            "Düşmemeye çalış!"
        ]

        y_pos = 150
        for instr in instructions:
            instr_text = font.render(instr, True, WHITE)
            instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            screen.blit(instr_text, instr_rect)
            y_pos += 40

        # Geri dönüş talimatını çiz
        back_text = font.render("ESC ile menüye dön", True, GREEN)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        screen.blit(back_text, back_rect)

        # Yanıp sönen çerçeve efekti (500ms açık, 500ms kapalı)
        if pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.rect(screen, WHITE, back_rect.inflate(20, 10), 2)

    def draw_menu(self):
        """
        Ana menüyü ekrana çizer.
        Oyun başlığı, yüksek skor ve başlatma seçenekleri içerir.
        """
        # Arka planı çiz
        screen.blit(bg_image, (0, 0))

        # Oyun başlığını çiz
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("JUMPY TOWER", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)

        # Yüksek skor görselini ve değerini çiz
        try:
            # Yüksek skor görselini yüklemeye çalış
            original_img = pygame.image.load("assets/high_scores.png").convert_alpha()
            original_width = original_img.get_width()
            original_height = original_img.get_height()
            new_width = 200
            new_height = int(original_height * (new_width / original_width))
            high_scores_img = pygame.transform.scale(original_img, (new_width, new_height))
            high_scores_rect = high_scores_img.get_rect(center=(SCREEN_WIDTH // 2, 250))
            screen.blit(high_scores_img, high_scores_rect)

            # Skor değerini çiz
            score_value = font.render(f"{self.high_score}", True, YELLOW)
            score_rect = score_value.get_rect(center=(SCREEN_WIDTH // 2, high_scores_rect.bottom + 30))
            screen.blit(score_value, score_rect)
        except Exception as e:
            # Görsel yüklenemezse basit metin göster
            print("High scores image couldn't be loaded:", e)
            high_score_text = font.render(f"En Yüksek Skor: {self.high_score}", True, YELLOW)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
            screen.blit(high_score_text, high_score_rect)

        # Başlatma talimatını çiz
        start_text = font.render("ENTER ile başlat", True, GREEN)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        screen.blit(start_text, start_rect)

        # Yardım talimatını çiz
        help_text = font.render("H tuşu ile oynanış", True, WHITE)
        help_rect = help_text.get_rect(center=(SCREEN_WIDTH // 2, 390))
        screen.blit(help_text, help_rect)

        # Yanıp sönen çerçeve efekti (başlatma butonu için)
        if pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.rect(screen, WHITE, start_rect.inflate(20, 10), 2)

    def handle_menu_events(self):
        """
        Ana menüdeki olayları (tuş basımları vb.) işler.

        Dönüş:
        - True: Oyundan çıkılacak
        - False: Oyun devam edecek
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True  # Oyundan çık

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # ENTER tuşuna basıldığında
                    self.in_menu = False
                    self.game_active = True  # Oyunu başlat
                elif event.key == pygame.K_h:  # H tuşuna basıldığında
                    self.in_menu = False
                    self.in_help = True  # Yardım ekranını göster

        return False  # Oyun devam etsin

    def handle_help_events(self):
        """
        Yardım ekranındaki olayları işler.

        Dönüş:
        - True: Oyundan çıkılacak
        - False: Oyun devam edecek
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True  # Oyundan çık

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC tuşuna basıldığında
                    self.in_help = False
                    self.in_menu = True  # Ana menüye dön

        return False  # Oyun devam etsin

    def run_game(self):
        """
        Asıl oyun döngüsünü çalıştırır.
        Oyun hızını, kamera hareketini ve oyun mantığını yönetir.
        """
        global game_speed

        # Oyun nesnelerini oluştur
        self.blocks = self.create_blocks()
        self.player = Player(self.blocks)

        # Oyun hızı ayarları
        game_speed = 1.5  # Başlangıç hızı
        max_game_speed = 2.9  # Maksimum hız
        speed_increase_rate = 0.0003  # Hız artış oranı

        # Zaman kontrolü için saat nesnesi
        clock = pygame.time.Clock()

        run = True
        scroll = 0  # Kaydırma miktarı

        # Kamera ayarları
        camera_min_offset = 150  # Minimum kamera ofseti
        camera_safe_zone = SCREEN_HEIGHT // 2  # Güvenli bölge (ekranın ortası)

        while run and self.game_active:
            # Arka planı çiz
            screen.blit(bg_image, (0, 0))

            # Klavye durumunu al
            keys = pygame.key.get_pressed()

            # Oyuncuyu güncelle
            self.player.update(keys, self.blocks)

            # Oyuncu yükselmeye başladıysa hızı arttır
            if self.player.start_scroll and game_speed < max_game_speed:
                game_speed += speed_increase_rate

            # Kamera hareketi ve kaydırma
            if self.player.start_scroll:
                min_top_distance = camera_min_offset
                player_screen_pos = self.player.rect.y - scroll

                # Oyuncu takla atıyorsa farklı kamera davranışı
                if self.player.flipping:
                    target_camera_y = self.player.rect.y - camera_safe_zone + 100
                    camera_speed = 0.2
                else:
                    # Oyuncu yukarı hareket ediyorsa
                    if self.player.vel_y < 0:
                        camera_offset = self.player.camera_offset
                        camera_speed = self.player.camera_speed_up * 1.5
                    else:  # Oyuncu aşağı hareket ediyorsa
                        camera_offset = min(self.player.camera_offset, 150)
                        camera_speed = self.player.camera_speed_down * 1.2

                    target_camera_y = self.player.rect.y - camera_safe_zone + camera_offset

                # Kamera pozisyonunu yumuşak bir şekilde güncelle
                self.player.camera_y += (target_camera_y - self.player.camera_y) * camera_speed

                # Takla durumuna göre kaydırma hızını ayarla
                if self.player.flipping:
                    scroll = 2.0 * game_speed
                else:
                    scroll = 1.5 * game_speed

                # Oyuncu ekranın üst kısmına çok yaklaşırsa acil düzeltme yap
                if player_screen_pos < min_top_distance:
                    immediate_correction = min_top_distance - player_screen_pos
                    self.player.camera_y -= immediate_correction

                camera_scroll = scroll
            else:
                # Oyun başlangıcında kaydırma yok
                scroll = 0
                camera_scroll = 0

            # Blokları güncelle ve çiz
            for block in self.blocks:
                block.update(camera_scroll, self.blocks)
                # Sadece ekranda görünen blokları çiz (performans için)
                if block.rect.bottom >= 0 and block.rect.top <= SCREEN_HEIGHT:
                    block.draw(screen)

            # Oyuncuyu çiz
            self.player.draw(screen)

            # Yüksek skoru güncelle
            if self.player.score > self.high_score:
                self.high_score = self.player.score
                self._save_high_score(self.high_score)

            # Oyuncu ekranın altından çıkarsa oyunu bitir
            if self.player.rect.top > SCREEN_HEIGHT + 100:
                self.game_active = False
                self.in_menu = True

            # Olayları işle
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # ESC ile menüye dön
                        run = False
                        self.game_active = False
                        self.in_menu = True

            # Ekranı güncelle
            pygame.display.update()

            # FPS sınırı (60 FPS)
            clock.tick(60)

    def run(self):
        """
        Oyun ana döngüsünü çalıştırır.
        Menü, yardım ekranı ve oyun arasında geçişleri yönetir.
        """
        quit_game = False

        while not quit_game:
            if self.in_menu:
                # Ana menüdeyse
                self.draw_menu()
                quit_game = self.handle_menu_events()
            elif self.in_help:
                # Yardım ekranındaysa
                self.draw_help_menu()
                quit_game = self.handle_help_events()
            elif self.game_active:
                # Oyun aktifse
                self.run_game()

            # Ekranı güncelle
            pygame.display.update()


# Ana program başlangıç noktası
if __name__ == "__main__":
    game = GameManager()  # Oyun yöneticisini oluştur
    game.run()  # Oyunu başlat
    pygame.quit()  # Pygame'i kapat ve programdan çık