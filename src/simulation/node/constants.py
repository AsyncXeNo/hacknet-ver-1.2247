from simulation.fs import RootDir, File, Directory


BASE_FS = RootDir([
    Directory('bin', [], 0),

    Directory('boot', [
        File('vmlinuz', b'', 0),
        File('initrd.img', b'', 0),
    ], 0),

    Directory('etc', [
        File('passwd', b'root:x:0:0:System Administrator:/root:/bin/bash\n', 0),
        File('shadow', b'root:{password}:::::::\n', 0),
        File('hostname', b'', 0),
    ], 0),

    Directory('home', [], 0),

    Directory('log', [], 0),

    Directory('media', [], 0),

    Directory('root', [], 0),

    Directory('sys', [], 0),

    Directory('tmp', [], 0),
])