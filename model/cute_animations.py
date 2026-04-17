"""
Cute Walking Animation Characters for Loading
Sử dụng Unicode characters để tạo animation người/nhân vật đi bộ
"""

# ===== WALKING PERSON ANIMATIONS =====

# 1. Simple Walking Person (Black & White)
WALKING_PERSON = ["🚶", "🚶‍♂️", "🚶‍♀️", "🚶"]

# 2. Running Person (Faster!)
RUNNING_PERSON = ["🏃", "🏃‍♂️", "🏃‍♀️", "🏃"]

# 3. Dancing Person (Fun!)
DANCING_PERSON = ["💃", "🕺", "💃", "🕺"]

# 4. Cute Girl Walking
GIRL_WALKING = ["🚶‍♀️", "💁‍♀️", "🙋‍♀️", "💁‍♀️"]

# 5. Cat Walking (Kawaii!)
CAT_WALKING = ["🐱", "🐈", "😺", "😸"]

# 6. Bunny Hopping
BUNNY_HOPPING = ["🐰", "🐇", "🐰", "🐇"]

# 7. Bear Walking
BEAR_WALKING = ["🐻", "🧸", "🐻", "🧸"]

# 8. Sparkle Trail (Magic!)
SPARKLE_TRAIL = ["✨", "💫", "⭐", "🌟"]

# 9. Heart Trail (Love!)
HEART_TRAIL = ["💕", "💖", "💗", "💝"]

# 10. Flower Trail (Spring!)
FLOWER_TRAIL = ["🌸", "🌺", "🌻", "🌼"]

# ===== COMBINED ANIMATIONS =====

# Girl + Hearts
GIRL_HEARTS = [
    "🚶‍♀️💕",
    "💁‍♀️💖", 
    "🙋‍♀️💗",
    "💁‍♀️💝"
]

# Cat + Sparkles
CAT_SPARKLES = [
    "🐱✨",
    "😺💫",
    "😸⭐",
    "😻🌟"
]

# Running + Speed Lines
RUNNING_FAST = [
    "💨🏃",
    "🏃💨",
    "💨🏃‍♀️",
    "🏃‍♀️💨"
]

# ===== PROGRESS INDICATORS =====

# Loading Dots
LOADING_DOTS = [
    "●○○○",
    "○●○○",
    "○○●○",
    "○○○●"
]

# Loading Arrows
LOADING_ARROWS = [
    "→   ",
    " →  ",
    "  → ",
    "   →"
]

# Loading Spinner
LOADING_SPINNER = ["◐", "◓", "◑", "◒"]

# Loading Bars
LOADING_BARS = [
    "▁▁▁▁",
    "▂▁▁▁",
    "▃▂▁▁",
    "▄▃▂▁"
]

# ===== CUTE CHARACTER SETS =====

# Hello Kitty Style
HELLO_KITTY_SET = [
    "🐱",  # Cat face
    "🎀",  # Ribbon
    "💕",  # Hearts
    "✨",  # Sparkles
    "🌸",  # Flower
    "💖",  # Sparkling heart
    "🐱",  # Cat again
    "💝"   # Heart with ribbon
]

# Princess Style
PRINCESS_SET = [
    "👸",  # Princess
    "👑",  # Crown
    "💎",  # Diamond
    "✨",  # Sparkles
    "🌹",  # Rose
    "💖",  # Heart
]

# Magical Girl Style
MAGICAL_GIRL_SET = [
    "🧚‍♀️",  # Fairy
    "✨",  # Sparkles
    "🌟",  # Star
    "💫",  # Dizzy
    "⭐",  # Star
    "🪄",  # Magic wand
]

# ===== RECOMMENDED FOR STATUS BAR =====

# Best for compact space
STATUS_BAR_COMPACT = [
    "🚶‍♀️",  # Walking girl
    "💕",  # Heart
    "🎀",  # Ribbon
    "✨"   # Sparkle
]

# Best for visibility
STATUS_BAR_VISIBLE = [
    "🏃‍♀️",  # Running girl
    "💖",  # Big heart
    "🌸",  # Flower
    "⭐"   # Star
]

# Best for cuteness
STATUS_BAR_CUTE = [
    "🐱",  # Cat
    "😺",  # Happy cat
    "💕",  # Hearts
    "🎀"   # Ribbon
]

# ===== USAGE EXAMPLES =====

if __name__ == "__main__":
    print("🎨 Cute Walking Animation Characters")
    print("=" * 50)
    
    print("\n1. Walking Person:")
    print(" ".join(WALKING_PERSON))
    
    print("\n2. Running Person:")
    print(" ".join(RUNNING_PERSON))
    
    print("\n3. Dancing Person:")
    print(" ".join(DANCING_PERSON))
    
    print("\n4. Girl + Hearts:")
    print(" ".join(GIRL_HEARTS))
    
    print("\n5. Cat + Sparkles:")
    print(" ".join(CAT_SPARKLES))
    
    print("\n6. Hello Kitty Set:")
    print(" ".join(HELLO_KITTY_SET))
    
    print("\n7. Loading Spinner:")
    print(" ".join(LOADING_SPINNER))
    
    print("\n8. Status Bar Cute:")
    print(" ".join(STATUS_BAR_CUTE))
