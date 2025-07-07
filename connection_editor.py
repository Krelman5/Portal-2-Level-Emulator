import pygame
import json

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

with open('level.json') as f:
    items = json.load(f)

# Just a simple layout
positions = {}
for idx, item in enumerate(items):
    positions[item['ID']] = (100 + (idx % 5) * 120, 100 + (idx // 5) * 120)

running = True
selected_source = None

while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for item_id, item_pos in positions.items():
                rect = pygame.Rect(item_pos[0]-20, item_pos[1]-20, 40, 40)
                if rect.collidepoint(pos):
                    if not selected_source:
                        selected_source = item_id
                    else:
                        if 'Targets' not in [i for i in items if i['ID'] == selected_source][0]:
                            [i for i in items if i['ID'] == selected_source][0]['Targets'] = []
                        [i for i in items if i['ID'] == selected_source][0]['Targets'].append(item_id)
                        selected_source = None

    # Draw nodes
    for item_id, pos in positions.items():
        color = (200, 50, 50) if item_id == selected_source else (200, 200, 200)
        pygame.draw.circle(screen, color, pos, 20)
        font = pygame.font.SysFont(None, 20)
        txt = font.render(item_id, True, (255, 255, 0))
        screen.blit(txt, (pos[0]-20, pos[1]+25))

    # Draw connections
    for item in items:
        if 'Targets' in item:
            for tgt in item['Targets']:
                pygame.draw.line(screen, (50, 200, 50), positions[item['ID']], positions[tgt], 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# Save updated JSON
with open('level.json', 'w') as f:
    json.dump(items, f, indent=4)

