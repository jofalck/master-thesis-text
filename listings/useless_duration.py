            else:
                assert False, "Unknown video FPS."
            # get video duration if available
            if 'duration' in value:
                duration = value['duration']
            else:
                duration = 1e8
                         'duration' : duration,
                     'duration'        : video_item['duration'],