from PIL import Image, ImageDraw, ImageFont
import math

def create_logo():
    # Create a blank image with transparent background
    size = (512, 512)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Gradient background circle
    # Simulating a radial gradient...
    center_x, center_y = size[0] // 2, size[1] // 2
    radius = 240
    
    # Outer glow / halo effect
    for r in range(radius, radius - 20, -1):
        alpha = int(255 * (1 - (radius - r) / 20))
        draw.ellipse(
            (center_x - r, center_y - r, center_x + r, center_y + r),
            fill=(28, 28, 30, alpha) # Dark grey halo
        )
    
    # Main Circle Concept: Dark but distinct
    draw.ellipse(
        (center_x - radius + 10, center_y - radius + 10, center_x + radius - 10, center_y + radius - 10),
        fill=(10, 10, 12, 255),
        outline=(60, 60, 65),
        width=2
    )
    
    # Geometric Bird / Eagle shape
    # Defining points for a modern, sleek bird silhouette
    # Using a polygon approach
    
    bird_color = (138, 43, 226) # Blue-Violet
    beak_color = (255, 165, 0) # Orange
    
    # Simplified modern bird shape (abstract)
    points = [
        (150, 300), # Tail tip
        (220, 250), # Lower body
        (350, 180), # Head top
        (400, 210), # Beak tip
        (360, 240), # Neck/throat
        (300, 350), # Wing tip
        (250, 320), # Belly
        (150, 300)  # Close
    ]
    
    # Let's try a better shape (Eagle head profile)
    # Head Top: (200, 150) -> (350, 150)
    # Beak: (350, 150) -> (420, 200) -> (350, 220)
    # Neck: (350, 220) -> (300, 400)
    # Back: (300, 400) -> (200, 400) -> (200, 150)
    
    eagle_head = [
        (180, 160), # Top back
        (320, 160), # Top head
        (380, 210), # Beak top
        (420, 230), # Beak point
        (370, 260), # Beak bottom
        (320, 250), # Mouth corner
        (280, 380), # Neck front
        (160, 380), # Neck back
        (180, 160)  # Close
    ]
    
    # Draw Eagle Head Silhouette
    draw.polygon(eagle_head, fill=(255, 255, 255, 255)) # White silhouette base
    
    # Inner detail (Dark fill to create shape)
    eagle_inner = [
        (190, 170),
        (310, 170),
        (360, 215), # Beak start
        (310, 245),
        (270, 370),
        (170, 370),
        (190, 170)
    ]
    # draw.polygon(eagle_inner, fill=(20, 20, 22, 255))
    
    # Actually, simpler is better. A blue sleek bird icon.
    # Triangle dynamic shape.
    
    # Wing 1
    draw.polygon([(100, 300), (256, 100), (412, 300), (256, 250)], fill=(94, 92, 230, 255))
    
    # Body/Head center (Circle)
    draw.ellipse((220, 180, 292, 252), fill=(10, 132, 255, 255))
    
    # Beak (Orange Triangle)
    draw.polygon([(280, 200), (340, 216), (280, 232)], fill=(255, 159, 10, 255))
    
    # Eye
    draw.ellipse((250, 205, 265, 220), fill=(255, 255, 255, 255))

    # Save
    image.save("assets/logo.png", "PNG")
    print("Logo generated successfully at assets/logo.png")

if __name__ == "__main__":
    create_logo()
