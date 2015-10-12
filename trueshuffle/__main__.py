# trueshuffle

# Auto-fill a disk with a revolving, intelligent shuffle

MANIFEST_NAME = 'trueshuffle.yaml'
FLOOR_FSPACE = 1 * 1000 * 1000 # Leave a meg left (manifest, et al)

def main():
    import argparse
    import logging
    import os
    import os.path
    import psutil
    import random
    import re
    import shutil
    import yaml

    FILES_RE = re.compile(r'.*\.(mp3|ogg|flac|wma)$', re.I)

    parser = argparse.ArgumentParser()
    parser.add_argument('destination')
    parser.add_argument('heard', nargs='?', type=int, default=0)
    parser.add_argument('--library', '-l', default=os.getcwd())
    parser.add_argument('--reshuffle', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--quiet', '-q', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif not args.quiet:
        logging.basicConfig(level=logging.INFO)

    logging.debug('Checking for existing shuffle manifest')
    manifestpath = os.path.join(args.destination, MANIFEST_NAME)
    manifest = {}
    if not args.reshuffle and os.path.exists(manifestpath):
        logging.info('Loading shuffle manifest')
        manifestf = open(manifestpath, 'r')
        manifest = yaml.load(manifestf)
        manifestf.close()

    if not manifest and args.heard:
        logging.error('Provided a rotate count but no manifest was found')
        return

    if manifest and not args.heard:
        logging.warn('Heard count not provided for rotation, may not have space')
    
    logging.info('Enumerating library (this may take a while)')
    library = []
    for root, dirs, files in os.walk(args.library):
        if '__MACOSX' in dirs:
            dirs.remove('__MACOSX')

        for filename in files:
            if FILES_RE.match(filename):
                path = os.path.join(root, filename)
                if path not in manifest:
                    logging.debug(path)
                    library.append(path)

    logging.info('Rotating out heard songs')
    highest = 0
    for filename in os.listdir(args.destination):
        bn = os.path.splitext(os.path.basename(filename))[0]
        count = None
        try:
            count = int(bn)
        except ValueError:
            pass
        highest = max(highest, count)
        if count and count < args.heard:
            path = os.path.join(args.destination, filename)
            logging.debug(path)
            os.remove(path)
    logging.debug('Highest song ID: %08d' % highest)

    fspace = psutil.disk_usage(args.destination).free
    logging.info('Free space on destination: %d' % fspace)
    fspace -= FLOOR_FSPACE
    logging.info('Shuffling new files to destination')

    while True:
        if fspace <= 0:
            logging.debug('Out of space')
            break
        if not library:
            logging.debug('Out of files to shuffle')
            break

        libfile = random.choice(library)
        library.remove(libfile)

        size = 0
        try: # failing on some unicode names
            size = os.path.getsize(libfile)
        except:
            logging.warn('Could not get file size: %s' % libfile)

        if size > fspace:
            logging.debug('%s: %d > %d' % (libfile, size, fspace))
            break

        # TODO: Transcode support
        highest += 1
        newbn = '%08d%s' % (highest, os.path.splitext(libfile)[1])
        manifest[libfile] = newbn
        logging.debug('%s => %s' % (libfile, newbn))
        try:
            shutil.copy(libfile, os.path.join(args.destination, newbn))
        except:
            logging.warn('Could not copy: %s' % libfile)

        if highest % 20 == 0:
            logging.info('Updating manifest')
            manifestf = open(manifestpath, 'w')
            manifestf.write(yaml.dump(manifest))
            manifestf.close()

        fspace = psutil.disk_usage(args.destination).free
        logging.debug('Free space on destination: %d' % fspace)
        fspace -= FLOOR_FSPACE

    logging.info('Updating manifest')
    manifestf = open(manifestpath, 'w')
    manifestf.write(yaml.dump(manifest))
    manifestf.close()

if __name__ == "__main__":
    main()

# vim: ai et ts=4 sts=4 sw=4
