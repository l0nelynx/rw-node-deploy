#!/bin/sh
set -eu
python3 -c 'import zipfile; z=zipfile.ZipFile("generated-site.zip", "w"); z.write("index.html"); z.close()'
