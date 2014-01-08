import math
import glob
import os
from subprocess import call, check_output
import shutil
import logging

from config import TARGET_SECONDS, HOME_DIR, LOG_FILE

import redis
redis = redis.StrictRedis()

logging.basicConfig(filename=LOG_FILE, level=logging.WARNING)

os.chdir(HOME_DIR)

while 1:
    id = redis.blpop('video')[1]

    logging.warning(os.environ['PATH'])
    logging.warning(os.environ['HOME'])

    # Get each frames time
    try:
        a = check_output(['identify', '-format', '"Frame %s: %Tcs\n"', 'uploads/' + id + '.gif'])
    except:
        logging.warning('identify error')
        redis.set(id, 'error')
        continue

    lengths = []

    for l in a.split('\n'):
        if ': ' in l:
            lengths.append(l.split(': ')[1])

    if not len(lengths):
        logging.warning('lengths error')
        redis.set(id, 'error')
        continue

    # Convert times to seconds
    seconds = []

    for t in lengths:
        if 'cs' in t:
            t = t.split('cs')[0]
            seconds.append(float(t) / float(100))

    if not len(seconds):
        logging.warning('seconds error')
        redis.set(id, 'error')
        continue

    loops = int(math.floor(TARGET_SECONDS / sum(seconds)))
    length = sum(seconds)

    # Explode gif to pngs
    try:
        b = call(['convert', '-coalesce', 'uploads/' + id + '.gif', 'uploads/' + id + '%05d.png'])
    except:
        logging.warning('convert error')
        redis.set(id, 'error')
        continue

    if len(set(seconds)) == 1:
        # Create video
        try:
            c = call(['ffmpeg', '-r', str(1 / seconds[0]), '-i', 'uploads/' + id + '%05d.png', '-vf', 'format=yuv420p', 'uploads/' + id + '_org.mp4'])
        except:
            logging.warning('ffmpeg error')
            redis.set(id, 'error')
            continue

        # Loop close to 30 seconds
        y = open('uploads/' + id + '.txt', 'w')

        for r in range(loops):
            y.write("file '" + id + str(r) + ".mp4'\n")
            shutil.copy2('uploads/' + id + '_org.mp4', 'uploads/' + id + str(r) + '.mp4')

        y.close()

        os.remove('uploads/' + id + '_org.mp4')

        try:
            d = call(['ffmpeg', '-f', 'concat', '-i', 'uploads/' + id + '.txt', '-c', 'copy', 'uploads/' + id + '.mp4'])
        except:
            logging.warning('ffmpeg concat error')
            redis.set(id, 'error')
            continue

        # Clean up
        os.remove('uploads/' + id + '.txt')

        for r in range(loops):
            os.remove('uploads/' + id + str(r) + '.mp4')
    else:
        logging.warning('multiple frame durations error')
        redis.set(id, 'error')
        continue

    # Clean up
    for filename in glob.glob("uploads/" + id + "*.png"):
        os.remove(filename)

    redis.set(id, 'done')
