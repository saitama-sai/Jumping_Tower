import pygame
import random
import os
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
try:
    bg_image = pygame.image.load('assets/bg.png').convert_alpha()
except:
    bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_image.fill((50, 50, 80))
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
game_speed = 1.5
class Player(pygame.sprite.Sprite):
    def __init__(self, blocks):
        super().__init__()
        self.frames = {"idle": [], "run": [], "jump": [], "fall": [], "hit": [], "flip": []}
        self._load_frames()
        self.current_action = "idle"
        self.frame_index = 0
        self.image = self.frames["idle"][0] if self.frames["idle"] else pygame.Surface((64, 64))
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, blocks[0].rect.top + 1))
        self._init_physics()
        self._init_animation()
        self._init_gameplay_vars()
        self._init_score_vars()
    def _load_frames(self):
        for i in range(1, 7):
            try:
                img = pygame.image.load(f"assets/running_frame1-{i}.png").convert_alpha()
                self.frames["run"].append(pygame.transform.scale(img, (64, 64)))
            except Exception as e:
                print(f"Couldn't load running_frame1-{i}.png:", e)
        self._load_specific_frames()
    def _load_specific_frames(self):
        frame_paths = {
            "jump": ["assets/jump_up1.png"],
            "fall": ["assets/jump_fall1.png"],
            "hit": ["assets/frame-got-hit1.png"],
            "idle": ["assets/standing_frame1-1.png", "assets/standing_frame1-2.png"]
        }
        for action, paths in frame_paths.items():
            for path in paths:
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.frames[action].append(pygame.transform.scale(img, (64, 64)))
                except Exception as e:
                    print(f"Couldn't load {path}:", e)
        self._load_flip_frames()
    def _load_flip_frames(self):
        try:
            flip_img = pygame.image.load("assets/flip.png").convert_alpha()
            for i in range(4):
                rotated = pygame.transform.rotate(flip_img, i * 90)
                scaled = pygame.transform.scale(rotated, (64, 64))
                self.frames["flip"].append(scaled)
        except Exception as e:
            print("Couldn't load flip.png:", e)
            if self.frames["jump"] and len(self.frames["jump"]) > 0:
                for i in range(4):
                    flip_img = pygame.transform.rotate(self.frames["jump"][0], i * 90)
                    self.frames["flip"].append(flip_img)
            else:
                dummy = pygame.Surface((64, 64))
                dummy.fill(BLUE)
                self.frames["flip"].append(dummy)
    def _init_physics(self):
        self.camera_y = self.rect.y
        self.camera_offset = 250
        self.camera_speed_up = 0.15
        self.camera_speed_down = 0.05
        self.vel_y = 0
        self.vel_x = 0
        self.gravity_boost = 0
        self.movement_slowdown = 1.0
    def _init_animation(self):
        self.anim_timer = 0
        self.anim_speed = 5
        self.is_hit = False
        self.facing_right = True
    def _init_gameplay_vars(self):
        self.start_scroll = False
        self.can_jump = True
        self.is_jumping = False
        self.jump_pressed = False
        self.power = 0
        self.max_power = 90
        self.power_increase = 25
        self.power_decrease = 0.1
        self.flipping = False
        self.flip_timer = 0
        self.flip_duration = 20
        self.flip_jump_boost = -20
        self.blocks_jumped = 0
        self.consecutive_flips = 0
        self.flip_combo = 1.0
        self.wall_bounce = False
        self.last_jumped_block = None
        self.jump_count = 0
    def _init_score_vars(self):
        self.score = 0
        self.height_score = 0
        self.max_height = 0
    def update(self, keys, blocks):
        dx = 0
        dy = 0
        moving = False
        self._update_power()
        if self.flipping:
            dx = self._handle_flipping(keys, blocks)
        elif not self.is_hit:
            dx, moving = self._handle_normal_movement(keys, blocks)
            self._handle_jumping(keys, blocks)
            dy = self._apply_gravity()
            self._handle_screen_boundaries(dx)
        self.rect.x += dx
        self.rect.y += dy
        self._check_collision(blocks)
        self._update_animation_state(moving)
        self._check_block_landing(blocks)
        self._animate()
        self._update_score()
    def _update_power(self):
        if self.power > 0 and not self.flipping:
            self.power -= self.power_decrease
            if self.power < 0:
                self.power = 0
    def _handle_flipping(self, keys, blocks):
        self.flip_timer += 1
        self._check_wall_collision()
        dx = self.vel_x
        if self.flip_timer >= self.flip_duration:
            self._end_flip()
            return 0
        else:
            self.vel_y = self.flip_jump_boost
            if keys[pygame.K_LEFT]:
                self.vel_x -= 0.5
                self.facing_right = False
            if keys[pygame.K_RIGHT]:
                self.vel_x += 0.5
                self.facing_right = True
            self._clamp_velocity()
            return self.vel_x
    def _check_wall_collision(self):
        if self.rect.left <= 0:
            self._handle_wall_bounce(True)
        elif self.rect.right >= SCREEN_WIDTH:
            self._handle_wall_bounce(False)
    def _handle_wall_bounce(self, from_left):
        self.vel_x = abs(self.vel_x) * 1.2 if from_left else -abs(self.vel_x) * 1.2
        self.facing_right = True if from_left else False
        self.consecutive_flips += 1
        self.flip_combo += 0.5
        self.wall_bounce = True
        self.power += 5
        self.flip_duration += 10
        self.score += int(10 * self.flip_combo)
    def _end_flip(self):
        self.flipping = False
        self.flip_timer = 0
        self.vel_y = 2
        self.vel_x = 0
        if not self.wall_bounce:
            self.flip_combo = 1
        else:
            self.gravity_boost = 0.4
            self.movement_slowdown = 0.7
        self.wall_bounce = False
    def _clamp_velocity(self):
        if self.vel_x > 12:
            self.vel_x = 12
        if self.vel_x < -12:
            self.vel_x = -12
    def _handle_normal_movement(self, keys, blocks):
        move_speed = 5
        if hasattr(self, 'movement_slowdown') and self.movement_slowdown < 1.0:
            move_speed *= self.movement_slowdown
            self.movement_slowdown += 0.01
            if self.movement_slowdown > 1.0:
                self.movement_slowdown = 1.0
        dx = 0
        moving = False
        if keys[pygame.K_LEFT]:
            dx = -move_speed
            self.facing_right = False
            moving = True
        if keys[pygame.K_RIGHT]:
            dx = move_speed
            self.facing_right = True
            moving = True
        return dx, moving
    def _handle_jumping(self, keys, blocks):
        on_ground = self._on_ground(blocks)
        if on_ground:
            self._handle_landing()
        jump_key_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP]
        flip_key_pressed = keys[pygame.K_f]
        if jump_key_pressed and not self.jump_pressed and on_ground:
            self._perform_jump()
        if flip_key_pressed and self.power >= self.max_power * 0.9:
            self._start_flipping()
        self.jump_pressed = jump_key_pressed
    def _handle_landing(self):
        self.is_jumping = False
        if self.flip_combo > 1:
            self.flip_combo = 1
        if hasattr(self, 'gravity_boost') and self.gravity_boost > 0:
            self.gravity_boost = 0
    def _perform_jump(self):
        self.vel_y = -11
        self.is_jumping = True
        self.start_scroll = True
        self.power += self.power_increase
        if self.power > self.max_power:
            self.power = self.max_power
        self.last_jumped_block = None
        self.jump_count += 1
        self.score += 5
    def _apply_gravity(self):
        gravity = 0.6
        if hasattr(self, 'gravity_boost') and self.gravity_boost > 0:
            gravity += self.gravity_boost
            self.gravity_boost -= 0.01
            if self.gravity_boost < 0:
                self.gravity_boost = 0
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y = 10
        return self.vel_y
    def _handle_screen_boundaries(self, dx):
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right
    def _update_animation_state(self, moving):
        if self.flipping:
            self.current_action = "flip"
        elif not self.is_hit:
            if self.vel_y < 0:
                self.current_action = "jump"
            elif self.vel_y > 4:
                self.current_action = "fall"
            elif moving:
                self.current_action = "run"
            else:
                self.current_action = "idle"
        else:
            self.current_action = "hit"
    def _check_block_landing(self, blocks):
        for block in blocks:
            if self.rect.bottom <= block.rect.top and self.rect.bottom + self.vel_y >= block.rect.top:
                if self.rect.right > block.rect.left and self.rect.left < block.rect.right:
                    if self.flipping:
                        self.blocks_jumped += 1
                        self.score += int(5 * self.flip_combo)
                        self.power -= 5
                        if self.power < 0:
                            self.power = 0
                    elif block != self.last_jumped_block:
                        self.score += 3
                        self.last_jumped_block = block
    def _update_score(self):
        current_height = -self.rect.y
        if current_height > self.max_height:
            height_diff = current_height - self.max_height
            self.max_height = current_height
            floors_passed = int(height_diff / 130)
            if floors_passed > 0:
                self.height_score += floors_passed * 50
                self.score += floors_passed * 50
    def _start_flipping(self):
        self.flipping = True
        self.flip_timer = 0
        self.vel_y = self.flip_jump_boost
        self.blocks_jumped = 0
        if self.facing_right:
            self.vel_x = 6
        else:
            self.vel_x = -6
        self.power *= 0.7
        self.consecutive_flips = 0
        self.wall_bounce = False
    def _animate(self):
        if self.frames.get(self.current_action) and len(self.frames[self.current_action]) > 0:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index += 1
                if self.frame_index >= len(self.frames[self.current_action]):
                    if self.current_action != "hit":
                        self.frame_index = 0
                    else:
                        self.frame_index = len(self.frames[self.current_action]) - 1
            if self.frame_index < len(self.frames[self.current_action]):
                self.image = self.frames[self.current_action][self.frame_index]
            else:
                self.frame_index = 0
                self.image = self.frames[self.current_action][self.frame_index]
        else:
            self.image = pygame.Surface((64, 64))
            self.image.fill((255, 0, 0))
    def _on_ground(self, blocks):
        for block in blocks:
            if self.rect.bottom <= block.rect.top + 5 and self.rect.bottom >= block.rect.top - 10:
                if self.rect.right > block.rect.left and self.rect.left < block.rect.right:
                    return True
        return False
    def _check_collision(self, blocks):
        if self.flipping:
            return
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0 and self.rect.bottom <= block.rect.bottom:
                    self.rect.bottom = block.rect.top + 1
                    self.vel_y = 0
    def draw(self, surface):
        flipped_image = pygame.transform.flip(self.image, not self.facing_right, False)
        if self.flipping:
            if self.wall_bounce:
                scaled_image = pygame.transform.scale(flipped_image,
                                                      (int(flipped_image.get_width() * 1.5),
                                                       int(flipped_image.get_height() * 1.5)))
                surface.blit(scaled_image, (self.rect.centerx - scaled_image.get_width() // 2,
                                            self.rect.centery - scaled_image.get_height() // 2))
            else:
                surface.blit(flipped_image, self.rect)
            ghost_img = flipped_image.copy()
            ghost_img.set_alpha(100)
            offset = -10 if self.facing_right else 10
            surface.blit(ghost_img, (self.rect.x - offset, self.rect.y))
        else:
            surface.blit(flipped_image, self.rect)
        self._draw_ui(surface)
    def _draw_ui(self, surface):
        info_font = pygame.font.Font(None, 22)
        right_margin = SCREEN_WIDTH - 120
        speed_text = info_font.render(f"Hız: {game_speed:.1f}x", True, WHITE)
        surface.blit(speed_text, (right_margin, 10))
        score_text = info_font.render(f"Skor: {self.score}", True, WHITE)
        surface.blit(score_text, (right_margin, 25))
        power_bar_width = 80
        power_bar_height = 8
        power_bar_x = right_margin
        power_bar_y = 60
        pygame.draw.rect(surface, RED, (power_bar_x, power_bar_y, power_bar_width, power_bar_height))
        filled_width = int((self.power / self.max_power) * power_bar_width)
        if self.power >= self.max_power * 0.9:
            bar_color = (0, 255, 255)
            if pygame.time.get_ticks() % 500 < 250:
                bar_color = (255, 255, 0)
        else:
            bar_color = GREEN
        pygame.draw.rect(surface, bar_color, (power_bar_x, power_bar_y, filled_width, power_bar_height))
        pygame.draw.rect(surface, WHITE, (power_bar_x, power_bar_y, power_bar_width, power_bar_height), 1)

        # Display power text right above the power bar
        power_text = info_font.render(f"Power: {int(self.power)}/{self.max_power}", True, WHITE)
        surface.blit(power_text, (power_bar_x, power_bar_y - 18))

        # Only display combo if active
        if self.flip_combo > 1:
            combo_text = info_font.render(f"Combo: x{self.flip_combo:.1f}", True, YELLOW)
            surface.blit(combo_text, (power_bar_x, power_bar_y + 15))

        # Only display blocks jumped during flipping
        if self.flipping or self.blocks_jumped > 0:
            blocks_text = info_font.render(f"Bloklar: {self.blocks_jumped}", True, BLUE)
            surface.blit(blocks_text, (power_bar_x, power_bar_y + 35))

