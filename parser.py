import json

def parse_p2c(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    items = []
    current_item = {}
    inside_items = False
    inside_item_block = False

    for line in lines:
        line = line.strip().strip('"')

        if line == "Items":
            inside_items = True
            continue

        if inside_items:
            if line == "{":
                if not inside_item_block:
                    inside_item_block = True
                    current_item = {}
                continue

            if line == "}":
                if inside_item_block:
                    inside_item_block = False
                    items.append(current_item)
                else:
                    inside_items = False
                continue

            # It's a key-value line
            if inside_item_block:
                parts = line.split('" "')
                if len(parts) == 2:
                    key, value = parts
                    current_item[key] = value

    return items

if __name__ == "__main__":
    parsed_items = parse_p2c("example.p2c")
    with open("level.json", "w") as f:
        json.dump(parsed_items, f, indent=4)

    print(f"Parsed {len(parsed_items)} items. Saved to level.json.")

