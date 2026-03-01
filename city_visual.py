import pygame
import random

pygame.init()

# Screen
WIDTH, HEIGHT = 1100, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Adaptive Predictive Control Simulation")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18, bold=True)
title_font = pygame.font.SysFont("Arial", 22, bold=True)

# Colors
ROAD_COLOR = (40, 40, 40)
LANE_COLOR = (170, 170, 170)
TEXT_COLOR = (255, 255, 255)

# Lanes (Y positions)
LANES = [150, 250, 350, 450, 550]

# Vehicle types
VEHICLE_TYPES = [
    ("car", (0, 150, 255), 45, 28),
    ("truck", (255, 140, 0), 70, 35),
    ("bike", (0, 255, 100), 30, 20)
]

# Speed levels
NORMAL_SPEED = 1.5
SLOW_SPEED = 0.7
MAINTAIN_SPEED = 1.0

# Vehicle class
class Vehicle:
    def __init__(self, x, y, color, vtype, w, h):
        self.x = x
        self.y = y
        self.color = color
        self.type = vtype
        self.width = w
        self.height = h
        self.base_speed = NORMAL_SPEED + random.uniform(0.2, 0.5)
        self.speed = self.base_speed
        self.status = "🟢 GO"
        self.status_color = (0, 255, 0)

    def update(self, all_vehicles, congestion_zone):
        front_vehicle = None
        for v in all_vehicles:
            if v != self and v.y == self.y and v.x > self.x:
                if front_vehicle is None or v.x < front_vehicle.x:
                    front_vehicle = v

        # Detect nearby traffic
        nearby = [v for v in all_vehicles if abs(v.y - self.y) < 80 and abs(v.x - self.x) < 150]
        high_density = len(nearby) > 4

        # Congestion zones simulate real-world traffic events
        in_congestion = congestion_zone[0] < self.x < congestion_zone[1]

        # Adaptive logic
        if high_density or in_congestion:
            self.speed = SLOW_SPEED
            self.status = "🔴 SLOW"
            self.status_color = (255, 0, 0)
        elif front_vehicle and front_vehicle.x - self.x < 80:
            self.speed = MAINTAIN_SPEED
            self.status = "🟡 MAINTAIN"
            self.status_color = (255, 255, 0)
        else:
            self.speed = self.base_speed
            self.status = "🟢 GO"
            self.status_color = (0, 255, 0)

        self.x += self.speed
        if self.x > WIDTH + 50:
            self.x = -random.randint(300, 600)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y - self.height // 2, self.width, self.height), border_radius=5)
        pygame.draw.circle(screen, self.status_color, (int(self.x + self.width // 2), int(self.y - 20)), 8)
        label = font.render(self.status, True, TEXT_COLOR)
        screen.blit(label, (self.x - 10, self.y - 40))


# Initialize vehicles
vehicles = []
for lane_y in LANES:
    for i in range(6):
        vtype, color, w, h = random.choice(VEHICLE_TYPES)
        x = random.randint(-400, WIDTH - 100)
        vehicles.append(Vehicle(x, lane_y, color, vtype, w, h))

# Main loop
running = True
timer = 0
congestion_zone = [random.randint(200, 800), random.randint(850, 1050)]

while running:
    screen.fill(ROAD_COLOR)

    # Draw lane lines
    for y in LANES:
        pygame.draw.line(screen, LANE_COLOR, (0, y + 50), (WIDTH, y + 50), 2)

    # Change congestion zone periodically
    timer += 1
    if timer % 400 == 0:
        congestion_zone = [random.randint(150, 700), random.randint(850, 1050)]

    # Highlight congestion zone visually
    pygame.draw.rect(screen, (100, 0, 0), (congestion_zone[0], 100, congestion_zone[1] - congestion_zone[0], 500), 3)

    # Update & draw all vehicles
    for v in vehicles:
        v.update(vehicles, congestion_zone)
        v.draw(screen)

    # Title and principle text
    title = title_font.render("Adaptive Predictive Control Simulation", True, (255, 255, 0))
    screen.blit(title, (360, 20))

    principle = font.render(
        "Principle: Vehicles detect upcoming traffic density and adjust speed early to avoid sudden braking & save energy.",
        True, TEXT_COLOR)
    screen.blit(principle, (50, 580))

    # Legend box
    pygame.draw.rect(screen, (25, 25, 25), (20, 70, 370, 200), border_radius=10)
    screen.blit(font.render("Legend / Meaning:", True, TEXT_COLOR), (35, 85))

    # Vehicle types
    pygame.draw.rect(screen, (0, 150, 255), (40, 110, 25, 15))
    screen.blit(font.render("- Car", True, TEXT_COLOR), (75, 107))
    pygame.draw.rect(screen, (255, 140, 0), (40, 130, 25, 15))
    screen.blit(font.render("- Truck", True, TEXT_COLOR), (75, 127))
    pygame.draw.rect(screen, (0, 255, 100), (40, 150, 25, 15))
    screen.blit(font.render("- Bike", True, TEXT_COLOR), (75, 147))

    # Indicators
    pygame.draw.circle(screen, (255, 0, 0), (40, 180), 7)
    screen.blit(font.render("🔴 Slow down (High traffic ahead)", True, TEXT_COLOR), (60, 172))
    pygame.draw.circle(screen, (255, 255, 0), (40, 200), 7)
    screen.blit(font.render("🟡 Maintain speed (Medium traffic)", True, TEXT_COLOR), (60, 192))
    pygame.draw.circle(screen, (0, 255, 0), (40, 220), 7)
    screen.blit(font.render("🟢 Go (Free flow)", True, TEXT_COLOR), (60, 212))

    pygame.display.update()

    # Exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(60)

pygame.quit()
