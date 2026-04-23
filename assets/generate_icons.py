#!/usr/bin/env python3
"""Generate icon assets for Lumina AI."""

import os
from PIL import Image, ImageDraw

# Output directory
ICONS_DIR = "/home/ryan/Dev/Projects/Python/lumina-ai/assets/icons"
os.makedirs(ICONS_DIR, exist_ok=True)

SIZE = 24


def create_sun_icon():
    """Create a sun icon (for switching to light mode)."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Center circle
    center = SIZE // 2
    radius = 5
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=(17, 129, 200, 255)
    )

    # Rays
    ray_length = 8
    ray_width = 2
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        x1 = center + int(radius * math.cos(rad))
        y1 = center + int(radius * math.sin(rad))
        x2 = center + int((radius + ray_length) * math.cos(rad))
        y2 = center + int((radius + ray_length) * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(17, 129, 200, 255), width=ray_width)

    img.save(os.path.join(ICONS_DIR, "sun.png"))
    print("Created sun.png")


def create_moon_icon():
    """Create a moon icon (for switching to dark mode)."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Moon crescent
    draw.arc([4, 2, 20, 22], start=45, end=225, fill=(17, 129, 200, 255), width=2)

    # Fill part of the moon
    for y in range(6, 18):
        for x in range(8, 18):
            dist = ((x - 12) ** 2 + (y - 12) ** 2) ** 0.5
            if dist < 7:
                img.putpixel((x, y), (17, 129, 200, 255))

    img.save(os.path.join(ICONS_DIR, "moon.png"))
    print("Created moon.png")


def create_send_icon():
    """Create a send arrow icon."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Arrow pointing right/up-right
    points = [
        (6, 12),   # left
        (14, 6),   # top
        (14, 10),  # inner top
        (18, 12),  # right
        (14, 14),  # inner bottom
        (14, 18),  # bottom
    ]
    draw.polygon(points, fill=(255, 255, 255, 255))

    img.save(os.path.join(ICONS_DIR, "send.png"))
    print("Created send.png")


def create_settings_icon():
    """Create a gear/settings icon."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = SIZE // 2
    outer_radius = 9
    inner_radius = 5

    # Gear teeth
    for i in range(8):
        import math
        angle = math.radians(i * 45)
        x1 = center + int(outer_radius * math.cos(angle))
        y1 = center + int(outer_radius * math.sin(angle))
        x2 = center + int((outer_radius + 3) * math.cos(angle))
        y2 = center + int((outer_radius + 3) * math.sin(angle))
        draw.line([x1, y1, x2, y2], fill=(17, 129, 200, 255), width=2)

    # Center circle
    draw.ellipse(
        [center - inner_radius, center - inner_radius,
         center + inner_radius, center + inner_radius],
        fill=(17, 129, 200, 255)
    )

    # Hole in center
    draw.ellipse(
        [center - 2, center - 2, center + 2, center + 2],
        fill=(0, 0, 0, 0)
    )

    img.save(os.path.join(ICONS_DIR, "settings.png"))
    print("Created settings.png")


def create_prompts_icon():
    """Create a prompts/collection icon (list icon)."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Three horizontal lines representing a list
    y_positions = [7, 12, 17]
    for y in y_positions:
        draw.rectangle([5, y - 1, 18, y + 1], fill=(17, 129, 200, 255))

    # Dots on left
    dot_positions = [(5, 7), (5, 12), (5, 17)]
    for x, y in dot_positions:
        draw.ellipse([x, y - 1, x + 2, y + 1], fill=(17, 129, 200, 255))

    img.save(os.path.join(ICONS_DIR, "prompts.png"))
    print("Created prompts.png")


def create_clear_icon():
    """Create a clear/trash icon."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Trash can body
    draw.rectangle([7, 8, 17, 20], fill=(17, 129, 200, 255))

    # Lid
    draw.rectangle([5, 6, 19, 8], fill=(17, 129, 200, 255))

    # Handle
    draw.rectangle([10, 3, 14, 6], fill=(17, 129, 200, 255))

    # Lines on can
    draw.line([10, 11, 10, 17], fill=(0, 0, 0, 50), width=1)
    draw.line([14, 11, 14, 17], fill=(0, 0, 0, 50), width=1)

    img.save(os.path.join(ICONS_DIR, "clear.png"))
    print("Created clear.png")


def create_copy_icon():
    """Create a copy/clipboard icon."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Clipboard
    draw.rectangle([6, 4, 18, 20], fill=(17, 129, 200, 255))

    # Clip at top
    draw.rectangle([9, 2, 15, 6], fill=(17, 129, 200, 255))

    # Paper lines
    draw.line([9, 10, 15, 10], fill=(255, 255, 255, 200), width=1)
    draw.line([9, 13, 15, 13], fill=(255, 255, 255, 200), width=1)
    draw.line([9, 16, 13, 16], fill=(255, 255, 255, 200), width=1)

    img.save(os.path.join(ICONS_DIR, "copy.png"))
    print("Created copy.png")


if __name__ == "__main__":
    create_sun_icon()
    create_moon_icon()
    create_send_icon()
    create_settings_icon()
    create_prompts_icon()
    create_clear_icon()
    create_copy_icon()
    print("All icons created successfully!")
