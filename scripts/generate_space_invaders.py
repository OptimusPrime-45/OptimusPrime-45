
import os
import json
import urllib.request
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# CONFIGURATION
# -----------------------------

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

WIDTH = 1000
HEIGHT = 420

BACKGROUND = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (145, 145, 145)
DARK_GREY = (65, 65, 65)

OUTPUT = "assets/space-invaders.gif"

# -----------------------------
# FETCH GITHUB CONTRIBUTIONS
# -----------------------------

query = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

payload = {
    "query": query,
    "variables": {"username": USERNAME}
}

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

if "errors" in result:
    raise RuntimeError(result["errors"])

calendar = (
    result["data"]["user"]
    ["contributionsCollection"]
    ["contributionCalendar"]
)

total = calendar["totalContributions"]
weeks = calendar["weeks"]

# Convert contribution data into a grid.
contributions = []

for x, week in enumerate(weeks):
    for y, day in enumerate(week["contributionDays"]):
        contributions.append(
            (x, y, day["contributionCount"])
        )

# -----------------------------
# PIXEL ART ALIEN
# -----------------------------

ALIEN = [
    "00100",
    "10101",
    "11111",
    "11011",
    "01010"
]

def draw_alien(draw, x, y, color, scale=2):

    for row, line in enumerate(ALIEN):
        for col, pixel in enumerate(line):

            if pixel == "1":
                x1 = x + col * scale
                y1 = y + row * scale

                draw.rectangle(
                    [
                        x1,
                        y1,
                        x1 + scale - 1,
                        y1 + scale - 1
                    ],
                    fill=color
                )

# -----------------------------
# SPACESHIP
# -----------------------------

def draw_ship(draw, x, y):

    draw.rectangle(
        [x + 15, y, x + 25, y + 12],
        fill=WHITE
    )

    draw.rectangle(
        [x + 7, y + 12, x + 33, y + 20],
        fill=WHITE
    )

    draw.rectangle(
        [x, y + 20, x + 40, y + 26],
        fill=WHITE
    )

# -----------------------------
# CREATE ANIMATION
# -----------------------------

os.makedirs("assets", exist_ok=True)

frames = []

FONT = ImageFont.load_default()

for frame_number in range(8):

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BACKGROUND
    )

    draw = ImageDraw.Draw(img)

    # Title
    draw.text(
        (WIDTH // 2, 25),
        "SPACE INVADERS",
        font=FONT,
        fill=WHITE,
        anchor="mm"
    )

    draw.text(
        (WIDTH // 2, 48),
        "GITHUB CONTRIBUTION SYSTEM",
        font=FONT,
        fill=GREY,
        anchor="mm"
    )

    # Divider
    draw.line(
        (45, 70, WIDTH - 45, 70),
        fill=DARK_GREY,
        width=1
    )

    # Contribution alien formation
    cell_x = 16
    cell_y = 22

    start_x = (WIDTH - len(weeks) * cell_x) // 2
    start_y = 100

    for week, day, count in contributions:

        if count == 0:
            continue

        x = start_x + week * cell_x
        y = start_y + day * cell_y

        # More contributions = brighter alien
        brightness = min(255, 90 + count * 35)

        color = (
            brightness,
            brightness,
            brightness
        )

        # Slight animation movement
        offset = (frame_number % 2) * 1

        draw_alien(
            draw,
            x + offset,
            y,
            color
        )

    # Animated laser
    laser_x = 490 + (frame_number % 4) * 4

    laser_y = 300 - frame_number * 17

    draw.line(
        [
            (laser_x, laser_y),
            (laser_x, laser_y + 35)
        ],
        fill=WHITE,
        width=2
    )

    # Spaceship
    draw_ship(
        draw,
        WIDTH // 2 - 20,
        325
    )

    # Bottom information
    draw.line(
        (45, 370, WIDTH - 45, 370),
        fill=DARK_GREY,
        width=1
    )

    draw.text(
        (60, 390),
        f"SCORE: {total}",
        font=FONT,
        fill=WHITE
    )

    draw.text(
        (WIDTH - 60, 390),
        "LEVEL: 01",
        font=FONT,
        fill=GREY,
        anchor="ra"
    )

    frames.append(img)

# -----------------------------
# SAVE GIF
# -----------------------------

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=180,
    loop=0,
    optimize=True
)

print(f"Animation generated: {OUTPUT}")
print(f"Total contributions: {total}")
