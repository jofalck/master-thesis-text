FPS = 25 # Global FPS constant

# classes = ["PASS", "DRIVE", ...] # Full list of classes

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def process_directory(directory_path, all_databases):
    file_path = os.path.join(directory_path, "Labels-ball.json")
    data = read_json_file(file_path)
    annotations = []
    prev_min = None
    subset = None

    for event in data['annotations']:
        time_str = event['gameTime'].split('-')[1] # e.g., "00:30"
        min_val = int(time_str.split(':')[0])
        sec = int(time_str.split(':')[1])
        event_label = event['label'].upper()

        start_sec = max(0, sec - 1)
        end_sec   = min(sec + 1, 60) # Assuming 60s clip duration
        start_frame = int(start_sec * FPS)
        end_frame   = int(end_sec   * FPS)

        min_dict = {
            'label':        event_label,
            'segment':      [start_sec, end_sec],
            'segment_frame':[start_frame, end_frame],
        }

        if prev_min is None or min_val != prev_min:
            # If new minute, finalize previous clip (if any)
            if annotations: # Implies prev_min is not None
                clip_id = f"{os.path.basename(directory_path)}_clip_{prev_min+1}"
                all_databases['database'][clip_id] = {
                    'subset':     subset,
                    'duration':   60, # Assumed clip duration
                    'fps':        FPS,
                    'annotations':annotations
                }
            # Start new clip
            prev_min = min_val
            subset   = 'Validation' if random.random() < 0.8 else 'Test' # Example subset logic
            annotations = [min_dict]
        else: # Same minute, accumulate event
            annotations.append(min_dict)

    # After loop, write last accumulated minute if any
    if annotations:
        clip_id = f"{os.path.basename(directory_path)}_clip_{prev_min+1}"
        all_databases['database'][clip_id] = {
            'subset':     subset,
            'duration':   60,
            'fps':        FPS,
            'annotations':annotations
        }

if __name__ == '__main__':
    base_directory = "/path/to/SoccerNet/SN-BAS-2025" # Example path
    all_databases = {
        "version": "SN-BAS-2025",
        "database": {},
    }

    # Simplified directory traversal
    for item_name in os.listdir(base_directory):
        item_path = os.path.join(base_directory, item_name)
        if os.path.isdir(item_path): # Process if it's a directory
            process_directory(item_path, all_databases)

    output_file = "./sn_bas_condensed.json"
    with open(output_file, 'w') as f:
        json.dump(all_databases, f, indent=4)
    # print(f"Condensed database written to {output_file}")
