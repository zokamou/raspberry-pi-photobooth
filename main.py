import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

os.environ.setdefault("SDL_VIDEODRIVER", "wayland")

import pygame
from picamera2 import Picamera2
from libcamera import Transform


SCREEN_W, SCREEN_H = 800, 480
CAMERA_RES = (800, 480)
CAPTURE_RES = (1920, 1080)

COUNTDOWN_SECONDS = 5
PRINTING_MESSAGE_SECONDS = 2

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
HOME_IMAGE = ASSETS_DIR / "start-screen.png"

PHOTOS_DIR = Path.home() / "photobooth-photos"

STATE_WELCOME = "welcome"
STATE_COUNTDOWN = "countdown"
STATE_PRINTING = "printing"

POWER_BUTTON_RECT = pygame.Rect(
    SCREEN_W - 80,
    20,
    60,
    60,
)

POWER_HOLD_SECONDS = 3


def draw_centered_text(screen, text, font, y, color=(255, 255, 255)):
    label = font.render(text, True, color)
    rect = label.get_rect(center=(SCREEN_W // 2, y))
    screen.blit(label, rect)


def frame_to_surface(frame):
    surface = pygame.surfarray.make_surface(
        frame.swapaxes(0, 1)[:, :, ::-1]
    )

    return pygame.transform.scale(
        surface,
        (SCREEN_W, SCREEN_H),
    )


def draw_power_button(screen, font, hold_progress=0):
    pygame.draw.circle(
        screen,
        (255, 255, 255),
        POWER_BUTTON_RECT.center,
        26,
        width=3,
    )

    pygame.draw.line(
        screen,
        (255, 255, 255),
        (
            POWER_BUTTON_RECT.centerx,
            POWER_BUTTON_RECT.top + 10,
        ),
        (
            POWER_BUTTON_RECT.centerx,
            POWER_BUTTON_RECT.centery,
        ),
        width=4,
    )

    if hold_progress > 0:
        pygame.draw.arc(
            screen,
            (255, 255, 255),
            POWER_BUTTON_RECT.inflate(10, 10),
            0,
            6.283 * min(hold_progress, 1),
            width=4,
        )


def shutdown_pi():
    subprocess.run(
        ["sudo", "/sbin/shutdown", "-h", "now"]
    )


def capture_photo(
    picam2,
    preview_config,
    camera_transform,
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    photo_path = PHOTOS_DIR / f"photo_{timestamp}.jpg"

    capture_config = picam2.create_still_configuration(
        main={
            "size": CAPTURE_RES,
        },
        transform=camera_transform,
    )

    picam2.switch_mode_and_capture_file(
        capture_config,
        str(photo_path),
    )

    picam2.stop()
    picam2.configure(preview_config)
    picam2.start()

    return photo_path


def main():
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    picam2 = Picamera2()

    camera_transform = Transform(
        hflip=True,
    )

    preview_config = picam2.create_preview_configuration(
        main={
            "size": CAMERA_RES,
            "format": "RGB888",
        },
        transform=camera_transform,
    )

    picam2.configure(preview_config)
    picam2.start()

    pygame.init()

    screen = pygame.display.set_mode(
        (SCREEN_W, SCREEN_H),
        pygame.FULLSCREEN | pygame.NOFRAME,
    )

    pygame.display.set_caption("Thermal Photobooth")
    pygame.mouse.set_visible(False)

    home_image = pygame.image.load(
        str(HOME_IMAGE)
    ).convert()

    if home_image.get_size() != (SCREEN_W, SCREEN_H):
        home_image = pygame.transform.scale(
            home_image,
            (SCREEN_W, SCREEN_H),
        )

    countdown_font = pygame.font.Font(None, 160)
    status_font = pygame.font.Font(None, 64)
    power_font = pygame.font.Font(None, 24)

    state = STATE_WELCOME
    state_start = time.time()

    power_press_start = None

    running = True
    clock = pygame.time.Clock()

    while running:
        now = time.time()
        elapsed = now - state_start

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (
                    pygame.K_ESCAPE,
                    pygame.K_q,
                ):
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == STATE_WELCOME:
                    if POWER_BUTTON_RECT.collidepoint(event.pos):
                        power_press_start = now
                    else:
                        state = STATE_COUNTDOWN
                        state_start = now

            elif event.type == pygame.MOUSEBUTTONUP:
                power_press_start = None

        screen.fill((0, 0, 0))

        if state == STATE_WELCOME:
            screen.blit(
                home_image,
                (0, 0),
            )

            hold_progress = 0

            if power_press_start is not None:
                hold_duration = now - power_press_start
                hold_progress = hold_duration / POWER_HOLD_SECONDS

                if hold_duration >= POWER_HOLD_SECONDS:
                    screen.fill((0, 0, 0))

                    draw_centered_text(
                        screen,
                        "Shutting down...",
                        status_font,
                        SCREEN_H // 2,
                    )

                    pygame.display.flip()
                    shutdown_pi()
                    running = False

            draw_power_button(
                screen,
                power_font,
                hold_progress,
            )

        elif state == STATE_COUNTDOWN:
            frame = picam2.capture_array("main")
            surface = frame_to_surface(frame)

            screen.blit(
                surface,
                (0, 0),
            )

            remaining = COUNTDOWN_SECONDS - int(elapsed)

            if remaining > 0:
                draw_centered_text(
                    screen,
                    str(remaining),
                    countdown_font,
                    SCREEN_H // 2,
                )

            else:
                screen.fill((255, 255, 255))
                pygame.display.flip()
                pygame.time.wait(100)

                last_capture_path = capture_photo(
                    picam2,
                    preview_config,
                    camera_transform,
                )

                print(
                    f"Captured photo: {last_capture_path}"
                )

                state = STATE_PRINTING
                state_start = time.time()

        elif state == STATE_PRINTING:
            draw_centered_text(
                screen,
                "Printing...",
                status_font,
                SCREEN_H // 2,
            )

            if elapsed >= PRINTING_MESSAGE_SECONDS:
                state = STATE_WELCOME
                state_start = time.time()

        pygame.display.flip()
        clock.tick(30)

    picam2.stop()
    pygame.quit()


if __name__ == "__main__":
    main()