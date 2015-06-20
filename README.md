# trueshuffle

Shuffles the files of a music library to a destination such as a thumbdrive. It attempts to be a *true* shuffle by
storing a manifest list of all of the files that have previously been copied. It supports rotating through a subsection
of a full shuffle of the library a segment at a time.

It copies to files in a simple numbered sequence (00000001.mp3, 00000002.ogg, 00000003.mp3, etc) which means that a
playing device need only to support playing files by filename in order to maintain the shuffle. By noting the last
played file number the script can remove played files and rotate in new files to the shuffle destination. Files with
missing metadata can be looked up in the manifest to determine their originating path.
