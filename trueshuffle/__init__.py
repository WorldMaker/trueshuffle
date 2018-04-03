"""
trueshuffle
-----------

Shuffles the files of a music library to a destination such as a thumbdrive. It attempts to be a *true* shuffle by
storing a manifest list of all of the files that have previously been copied.
"""

if __name__ == 'main':
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from trueshuffle.__main__ import main
    main()
