# Turtle Physics Engine
# Because who needs Unity when you have turtles?

import turtle
import random
import math
import time

# Screen setup
wn = turtle.Screen()
wn.title("Turtle Physics Engine")
wn.bgcolor("black")
wn.setup(width=800, height=600)
wn.tracer(0)  # Turning off the tracer to manually control updates. Speed is key!

# Physics constants
GRAVITY = -0.2      # Because what goes up must come down... faster!
GROUND_LEVEL = -250 # The floor is lava... well, not really, but don't touch it.
LEFT_WALL = -380    # Left boundary. No political jokes here.
RIGHT_WALL = 380    # Right boundary. Still no political jokes.

# Lists to keep track of everything. Like Santa's naughty list, but for objects.
objects = []
gravity_wells = []

# Shape and color options. Because variety is the spice of life.
shapes = ["circle", "square", "triangle"]
colors = ["red", "green", "blue", "yellow", "purple", "orange", "white", "cyan", "magenta"]

# Gravity well class. For when you want to spice things up with some space-time curvature.
class GravityWell(turtle.Turtle):
    def __init__(self, x, y, strength=0.5):
        super().__init__(shape="circle")
        self.speed(0)
        self.penup()
        self.goto(x, y)
        self.color("white")  # Gravity wells are mysterious like that
        self.shapesize(stretch_wid=1, stretch_len=1)
        self.strength = strength  # The stronger the gravity, the more dramatic the attraction

# The main attraction: PhysicsObject class
class PhysicsObject(turtle.Turtle):
    def __init__(self, x, y, vx, vy, shape_type, color, size=20):
        super().__init__(shape=shape_type)
        self.speed(0)
        self.penup()
        self.goto(x, y)
        self.color(color)
        self.vx = vx  # Velocity in the x-direction
        self.vy = vy  # Velocity in the y-direction
        self.size = size  # Because size matters (in physics)
        self.shapesize(stretch_wid=size/20, stretch_len=size/20)
        self.is_dragged = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.bind_events()

    def bind_events(self):
        # Attaching event handlers like a boss
        self.onclick(self.start_drag)
        self.onrelease(self.end_drag)
        self.ondrag(self.dragging)

    def start_drag(self, x, y):
        self.is_dragged = True
        self.drag_offset_x = self.xcor() - x
        self.drag_offset_y = self.ycor() - y
        self.vx = 0  # Stopping the object mid-flight. Physics, who?
        self.vy = 0

    def dragging(self, x, y):
        self.goto(x + self.drag_offset_x, y + self.drag_offset_y)

    def end_drag(self, x, y):
        self.is_dragged = False

    def move(self):
        if self.is_dragged:
            return  # If we're dragging it, let the human do the moving

        # Apply gravity wells' influence. Because who doesn't like being pulled in multiple directions?
        for well in gravity_wells:
            dx = well.xcor() - self.xcor()
            dy = well.ycor() - self.ycor()
            distance = math.hypot(dx, dy)
            if distance < 200:  # Gravity wells have a range, unlike my Wi-Fi
                force = well.strength / (distance / 50)
                angle = math.atan2(dy, dx)
                self.vx += math.cos(angle) * force
                self.vy += math.sin(angle) * force

        # Gravity: It's not just a good idea; it's the law!
        self.vy += GRAVITY

        # Update position
        new_x = self.xcor() + self.vx
        new_y = self.ycor() + self.vy

        # Collision detection with the ground
        if new_y - self.size/2 <= GROUND_LEVEL:
            new_y = GROUND_LEVEL + self.size/2
            self.vy = -self.vy * 0.8  # Losing some energy because physics
            if abs(self.vy) < 1:
                self.vy = 0  # Let's not have objects jittering on the ground

        # Collision detection with walls
        if new_x - self.size/2 <= LEFT_WALL:
            new_x = LEFT_WALL + self.size/2
            self.vx = -self.vx * 0.8
        elif new_x + self.size/2 >= RIGHT_WALL:
            new_x = RIGHT_WALL - self.size/2
            self.vx = -self.vx * 0.8

        # Move the object to its new position
        self.goto(new_x, new_y)

    def check_collision(self, other):
        if self.is_dragged or other.is_dragged:
            return  # Let's not interfere with user interaction

        dx = other.xcor() - self.xcor()
        dy = other.ycor() - self.ycor()
        distance = math.hypot(dx, dy)
        min_distance = (self.size + other.size) / 2

        if distance < min_distance:
            # Collision detected! Time to do some math
            angle = math.atan2(dy, dx)
            total_mass = self.size + other.size

            # Conservation of momentum (simplified). Isaac Newton would be proud.
            u1 = (self.vx, self.vy)
            u2 = (other.vx, other.vy)
            m1 = self.size
            m2 = other.size

            v1 = (
                (u1[0]*(m1 - m2) + 2*m2*u2[0]) / total_mass,
                (u1[1]*(m1 - m2) + 2*m2*u2[1]) / total_mass
            )
            v2 = (
                (u2[0]*(m2 - m1) + 2*m1*u1[0]) / total_mass,
                (u2[1]*(m2 - m1) + 2*m1*u1[1]) / total_mass
            )

            self.vx, self.vy = v1
            other.vx, other.vy = v2

            # Adjust positions to prevent sticking together like overcooked spaghetti
            overlap = min_distance - distance
            self.goto(self.xcor() - math.cos(angle) * overlap / 2,
                      self.ycor() - math.sin(angle) * overlap / 2)
            other.goto(other.xcor() + math.cos(angle) * overlap / 2,
                       other.ycor() + math.sin(angle) * overlap / 2)

# Function to create physics objects
def create_object(x, y):
    vx = random.uniform(-2, 2)
    vy = random.uniform(0, 5)
    shape_type = random.choice(shapes)
    color = random.choice(colors)
    size = random.randint(20, 40)
    obj = PhysicsObject(x, y, vx, vy, shape_type, color, size)
    objects.append(obj)

# Function called when the screen is clicked
def on_click(x, y):
    # Check if clicked on a gravity well to remove it
    for well in gravity_wells:
        if well.distance(x, y) < 20:
            gravity_wells.remove(well)
            well.hideturtle()
            return
    # Otherwise, create a new physics object
    create_object(x, y)

# Function to create a gravity well
def create_gravity_well(x=None, y=None):
    if x is None or y is None:
        x = random.randint(-300, 300)
        y = random.randint(-200, 200)
    well = GravityWell(x, y)
    gravity_wells.append(well)

# Function to clear the screen
def clear_screen():
    for obj in objects:
        obj.hideturtle()
    objects.clear()
    for well in gravity_wells:
        well.hideturtle()
    gravity_wells.clear()

# Functions to adjust gravity
def increase_gravity():
    global GRAVITY
    GRAVITY -= 0.05  # More gravity, more problems

def decrease_gravity():
    global GRAVITY
    GRAVITY += 0.05  # Less gravity, less... weight?

# Function to draw the ground
def draw_ground():
    ground = turtle.Turtle()
    ground.hideturtle()
    ground.color("white")
    ground.penup()
    ground.goto(LEFT_WALL, GROUND_LEVEL)
    ground.pendown()
    ground.goto(RIGHT_WALL, GROUND_LEVEL)

# Function to draw the walls
def draw_walls():
    wall = turtle.Turtle()
    wall.hideturtle()
    wall.color("white")
    wall.penup()
    wall.goto(LEFT_WALL, GROUND_LEVEL)
    wall.pendown()
    wall.goto(LEFT_WALL, 300)
    wall.penup()
    wall.goto(RIGHT_WALL, GROUND_LEVEL)
    wall.pendown()
    wall.goto(RIGHT_WALL, 300)

# Function to set up the on-screen menu/instructions
def setup_menu():
    menu = turtle.Turtle()
    menu.hideturtle()
    menu.color("white")
    menu.penup()
    menu.goto(-370, 260)
    menu.write("Controls:\nClick: Create Shape\nG: Create Gravity Well\nC: Clear Screen\nUp/Down: Adjust Gravity",
               align="left", font=("Arial", 12, "normal"))

# Function to bind key presses
def on_key_press():
    wn.onkey(clear_screen, "c")
    wn.onkey(increase_gravity, "Up")
    wn.onkey(decrease_gravity, "Down")
    wn.onkey(create_gravity_well, "g")  # Let's make gravity wells more predictable
    wn.listen()

# Function to update the background (optional)
def update_background():
    # Here you can implement dynamic background changes
    pass  # Placeholder for your creativity

# Initial setup
draw_ground()
draw_walls()
setup_menu()
on_key_press()

wn.onclick(on_click)

# Main animation loop
while True:
    # Update physics objects
    for i, obj in enumerate(objects):
        obj.move()
        # Check for collisions with other objects
        for other_obj in objects[i+1:]:
            obj.check_collision(other_obj)

    # Update background (if you added anything fancy)
    update_background()

    wn.update()
    time.sleep(0.017)  # Because 60 FPS is the gold standard

wn.mainloop()
