import json
import sys
import random
import os

# add a global fps constant
FPS =25

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as err:
        print(f"Error reading JSON file: {err}", file=sys.stderr)
        sys.exit(1)

classes = [
    "PASS",
    "DRIVE",
    "HEADER",
    "HIGH PASS",
    "OUT",
    "CROSS",
    "THROW IN",
    "SHOT",
    "BALL PLAYER BLOCK",
    "PLAYER SUCCESSFUL TACKLE",
    "FREE KICK",
    "GOAL",
]

def process_directory(directory_path, all_databases):
    file_path = os.path.join(directory_path, "Labels-ball.json")
    if not os.path.exists(file_path):
        print(f"Labels file not found in {directory_path}", file=sys.stderr)
        return

    data = read_json_file(file_path)
    annotations = []
    prev_min = None
    subset = None

    for event in data['annotations']:
        time_str = event['gameTime'].split('-')[1]
        min_val = int(time_str.split(':')[0])
        sec = int(time_str.split(':')[1])

        event_label = event['label'].upper()

        binary_label = event['team']
        if binary_label == "right":
            bin = 1
        elif binary_label == "left":
            bin = 0

        # compute relative segment within the 60s clip
        start_sec = max(0, sec - 1)
        end_sec   = min(sec + 1, 60)
        start_frame = int(start_sec * FPS)
        end_frame   = int(end_sec   * FPS)

        min_dict = {
            'label':        event_label,
            'segment':      [start_sec, end_sec],
            'segment_frame':[start_frame, end_frame],
            'label_id':     (classes.index(event_label) if event_label in classes else -1),
        }

        # first event of this clip?
        if prev_min is None:
            prev_min = min_val
            subset   = 'Validation' if random.random() < 0.7 else 'Test'
            annotations.append(min_dict)

        # same minute => accumulate
        elif min_val == prev_min:
            annotations.append(min_dict)

        # new minute => write old clip, then restart
        else:
            clip_id = f"{os.path.basename(directory_path)}_clip_{prev_min+1}"
            all_databases['database'][clip_id] = {
                'subset':     subset,
                'duration':   60,
                'fps':        FPS,
                'annotations':annotations
            }
            # restart for the new minute
            prev_min = min_val
            subset   = 'Validation' if random.random() < 0.7 else 'Test'
            annotations = [min_dict]

    # after loop, write last minute if any
    if annotations:
        clip_id = f"{os.path.basename(directory_path)}_clip_{prev_min+1}"
        all_databases['database'][clip_id] = {
            'subset':     subset,
            'duration':   60,
            'fps':        FPS,
            'annotations':annotations
        }

if __name__ == '__main__':
    base_directory = "/cluster/home/jofa/master/data/raw/SoccerNet/SN-BAS-2025"
    all_databases = {
        "version": "SN-BAS-2025",
        "database": {},
    }

    for root, dirs, files in os.walk(base_directory):
        for directory in dirs:
            process_directory(os.path.join(root, directory), all_databases)

    output_file = "./sn_bas_2.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(all_databases, f, indent=4)
        print(f"Database written to {output_file}")
    except Exception as err:
        print(f"Error writing JSON file: {err}", file=sys.stderr)
        sys.exit(1)