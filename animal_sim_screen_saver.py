import pygame
import random
import math
import sys


# Surface Dimensions
WIDTH, HEIGHT = 600, 300


# Flexable parameters
SIM_SPEED = 2

starting_plants = 4
sun_intensity = 3

starting_animals = 2

plant_color = "green"

animal_color = "red"


# Array initiation

active_plants = []
active_animals = []


# Class initiation


class Plant:
    radius = 6
    baby_distance = 15

    def __init__(self, id, x, y, energy, health):
        self.id = id
        self.x = x
        self.y = y
        self.energy = energy
        self.health = health
        self.dead = False

        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def update(self, dt):
        self.think(dt)
        self.gain_energy()
        self.check_die()

    # Update collision box
    def update_rect(self):
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def think(self, dt):
        if self.energy > 80:
            self.make_baby(dt)

    def gain_energy(self):
        self.energy += sun_intensity * random.randint(0, 1)

    def make_baby(self, dt):

        hyp = self.baby_distance

        adj = random.randint(0, hyp)
        opp = math.sqrt(hyp * hyp - adj * adj)

        if random.choice((True, False)):
            adj = -adj
        if random.choice((True, False)):
            opp = -opp

        baby_x = self.x + adj
        baby_y = self.y + opp

        # 1) stay on screen
        if not (self.radius <= baby_x <= WIDTH - self.radius and
                self.radius <= baby_y <= HEIGHT - self.radius):
            return  # no spawn if off-screen

        # 2) don't overlap other plants
        baby_rect = pygame.Rect(
            baby_x - self.radius,
            baby_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        for p in active_plants:
            if baby_rect.colliderect(p.rect):
                return  # space not empty, don't spawn

        # 3) actually spawn
        spawn_new_plant(baby_x, baby_y)
        self.energy = 0

    def check_die(self):
        if self.health <= 0:
            self.dead = True


class Animal:
    radius = 5
    baby_distance = 20
    speed = 1
    velocity = [0, 0]
    mass = 10

    def __init__(self, id, x, y, energy, health):
        self.id = id
        self.x = x
        self.y = y
        self.energy = energy
        self.health = health
        self.dead = False

        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def update(self, dt):
        self.think(dt)
        self.spend_energy()
        self.check_die()
        self.update_rect()

    def update_rect(self):
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def think(self, dt):
        if self.energy > 5000:
            self.velocity[0] = 0
            self.velocity[1] = 0
            self.make_baby(dt)

        else:
            self.look_for_food(active_plants)

    def spend_energy(self):
        self.energy -= 1

    def eat(self, target):
        target.dead = True
        self.energy += target.energy

    def walk_prep(self, location):
        target_x, target_y = location

        if target_x > self.x:
            self.velocity[0] = self.speed
        elif target_x < self.x:
            self.velocity[0] = -self.speed
        else:
            self.velocity[0] = 0

        if target_y > self.y:
            self.velocity[1] = self.speed
        elif target_y < self.y:
            self.velocity[1] = -self.speed
        else:
            self.velocity[1] = 0

        # move
        self.x += self.velocity[0]
        self.y += self.velocity[1]

    def look_for_food(self, plants):
        if not plants:
            return

        nearest = None
        best_dist_sq = float("inf")

        # find nearest plant
        for p in plants:
            dx = p.x - self.x
            dy = p.y - self.y
            dist_sq = dx*dx + dy*dy

            if dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                nearest = p

        if nearest is None:
            return

        # true distance
        distance = math.sqrt(best_dist_sq)

        # if close enough, eat it
        eat_range = self.radius + nearest.radius
        if distance <= eat_range:
            self.eat(nearest)
        else:
            # otherwise walk towards it
            self.walk_prep((nearest.x, nearest.y))

    def make_baby(self, dt):
        hyp = self.baby_distance

        adj = random.randint(0, hyp)
        opp = math.sqrt(hyp * hyp - adj * adj)

        if random.choice((True, False)):
            adj = -adj
        if random.choice((True, False)):
            opp = -opp

        baby_x = self.x + adj
        baby_y = self.y + opp

        if not (self.radius <= baby_x <= WIDTH - self.radius and
                self.radius <= baby_y <= HEIGHT - self.radius):
            return

        baby_rect = pygame.Rect(
            baby_x - self.radius,
            baby_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        for a in active_animals:
            if baby_rect.colliderect(a.rect):
                return

        spawn_new_animal(baby_x, baby_y)
        self.energy = 2000

    def check_die(self):
        if self.energy <= 0:
            self.dead = True

        # population control
        for p in active_animals:
            if p is self:
                continue
            if self.rect.colliderect(p.rect):
                self.dead = True
                break


# Function initiation


def init_spawn_plants():

    num_plants = starting_plants
    plant_id = 0

    for plant_id in range(num_plants):
        plant_spawn_x = round(random.randint(0, WIDTH))
        plant_spawn_y = round(random.randint(0, HEIGHT))

        plant = Plant(plant_id, plant_spawn_x, plant_spawn_y, 10, 10)
        active_plants.append(plant)

        plant_id += 1


def init_spawn_animals():

    num_animals = starting_animals
    animal_id = 0

    for animal_id in range(num_animals):
        animal_spawn_x = round(random.randint(0, WIDTH))
        animal_spawn_y = round(random.randint(0, HEIGHT))

        animal = Animal(animal_id, animal_spawn_x, animal_spawn_y, 2000, 100)
        active_animals.append(animal)

        animal_id += 1


def spawn_new_plant(x, y):
    plant_id = len(active_plants)
    plant = Plant(plant_id, x, y, 10, 10)
    active_plants.append(plant)


def spawn_new_animal(x, y):
    animal_id = len(active_animals)
    animal = Animal(animal_id, x, y, 2000, 100)
    active_animals.append(animal)


def draw_plants(screen):
    for plant in active_plants:
        pygame.draw.circle(screen, plant_color,
                           (plant.x, plant.y), Plant.radius)


def draw_animals(screen):
    for animal in active_animals:
        pygame.draw.circle(
            screen, animal_color, (animal.x, animal.y), Animal.radius)


def main():
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("My Evolution Sim")

    init_spawn_plants()
    init_spawn_animals()

    running = True
    while running:

        dt = clock.tick(SIM_SPEED * 30) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("black")
        draw_plants(screen)
        draw_animals(screen)

        # update plants
        global active_plants
        active_plants = [p for p in active_plants if not p.dead]
        for plant in active_plants:
            plant.update(dt)

        # update animals
        global active_animals
        active_animals = [a for a in active_animals if not a.dead]
        for animal in active_animals:
            animal.update(dt)

        # respawn if needed
        if len(active_plants) < starting_plants:
            init_spawn_plants()
        if len(active_animals) < starting_animals:
            init_spawn_animals()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
