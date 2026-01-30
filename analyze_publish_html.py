#!/usr/bin/env python3
"""
Analyze the debug HTML to find publish button structure
"""
from bs4 import BeautifulSoup

with open("debug_publish_fail.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Find all buttons with "Publish" text
print("=" * 80)
print("SEARCHING FOR PUBLISH BUTTONS")
print("=" * 80)

all_buttons = soup.find_all('button')
publish_buttons = []

for btn in all_buttons:
    text = btn.get_text(strip=True).lower()
    if 'publish' in text or 'đăng' in text:
        publish_buttons.append(btn)
        
print(f"\nFound {len(publish_buttons)} buttons with 'Publish' text:\n")

for i, btn in enumerate(publish_buttons, 1):
    print(f"\n--- Button {i} ---")
    print(f"Text: {btn.get_text(strip=True)}")
    print(f"Classes: {btn.get('class', [])}")
    print(f"Aria-label: {btn.get('aria-label', 'N/A')}")
    print(f"Disabled: {btn.get('disabled', 'N/A')}")
    
    # Show parent structure
    parent = btn.parent
    depth = 0
    print("\nParent structure:")
    while parent and depth < 5:
        parent_class = parent.get('class', [])
        parent_id = parent.get('id', '')
        print(f"  {'  ' * depth}└─ <{parent.name}> class={parent_class} id={parent_id}")
        parent = parent.parent
        depth += 1

# Search for publish panel
print("\n" + "=" * 80)
print("SEARCHING FOR PUBLISH PANEL")
print("=" * 80)

panel = soup.find(class_="editor-post-publish-panel")
if panel:
    print("\n✅ Found .editor-post-publish-panel")
    print(f"Display style: {panel.get('style', 'N/A')}")
    print(f"Classes: {panel.get('class', [])}")
    
    # Find buttons inside panel
    panel_buttons = panel.find_all('button')
    print(f"\nButtons inside panel: {len(panel_buttons)}")
    for btn in panel_buttons:
        print(f"  - {btn.get_text(strip=True)} | class={btn.get('class', [])}")
else:
    print("\n❌ NO .editor-post-publish-panel found!")
    
    # Try alternative selectors
    print("\nSearching for alternatives...")
    
    # Check for any element with "publish" in class
    publish_elements = soup.find_all(class_=lambda x: x and 'publish' in ' '.join(x).lower())
    print(f"\nFound {len(publish_elements)} elements with 'publish' in class:")
    for elem in publish_elements[:10]:  # Show first 10
        print(f"  - <{elem.name}> class={elem.get('class', [])}")

# Check current URL/form action
print("\n" + "=" * 80)
print("CHECKING FORM/PAGE STATE")
print("=" * 80)

forms = soup.find_all('form')
print(f"\nFound {len(forms)} forms")
for form in forms[:5]:
    action = form.get('action', 'N/A')
    if 'post' in action:
        print(f"  - Action: {action}")

# Check for post ID
post_id_input = soup.find('input', {'name': 'post_ID'})
if post_id_input:
    print(f"\n✅ Post ID found: {post_id_input.get('value', 'N/A')}")
else:
    print("\n❌ No post_ID input found")

print("\n" + "=" * 80)
