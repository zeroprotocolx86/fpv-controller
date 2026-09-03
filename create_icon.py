from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background circle
        margin = size // 8
        draw.ellipse([margin, margin, size - margin, size - margin], fill="#1c2128", outline="#58a6ff", width=max(1, size // 32))

        # Play triangle (joystick feel)
        cx, cy = size // 2, size // 2
        r = size // 3
        # Left stick representation
        draw.ellipse([cx - r//2 - r//3, cy - r//3, cx - r//6, cy + r//3], fill="#f85149")
        # Right stick representation
        draw.ellipse([cx + r//6, cy - r//3, cx + r//2 + r//3, cy + r//3], fill="#3fb950")
        # Center dot
        draw.ellipse([cx - r//6, cy - r//6, cx + r//6, cy + r//6], fill="#58a6ff")

        images.append(img)

    # Save as .ico with multiple sizes
    ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
    os.makedirs(os.path.dirname(ico_path), exist_ok=True)

    images[-1].save(ico_path, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[:-1])
    print(f"Icon saved: {ico_path}")

    # Also save as .png for GitHub
    png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
    images[-1].save(png_path)
    print(f"PNG saved: {png_path}")

if __name__ == "__main__":
    create_icon()
