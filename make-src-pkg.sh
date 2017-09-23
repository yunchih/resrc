#!/usr/bin/env bash

VERSION=1.1
PKG_NAME=resrc
FILES=("bin" "examples" "resrc" "setup.py" "README.md")
BASE="$(dirname "$0")"
PKG_DIR="${BASE}/pkg"
PKG_NAME_FULL="${PKG_NAME}-${VERSION}"

cd "${BASE}"
mkdir -p "${PKG_DIR}/${PKG_NAME_FULL}"
for f in "${FILES[@]}"; do
    if [ -d "$f" ]; then
        find "$f" -regex "\(.*__pycache__.*\|*.py[co]\)" -delete
    fi

    cp -av "$f" "${PKG_DIR}/${PKG_NAME_FULL}"
done

tar -C "${PKG_DIR}" -zcvf "${PKG_NAME_FULL}.tar.gz" "${PKG_NAME_FULL}"

echo -n "MD5 sum = \""
echo -n $(md5sum "${PKG_NAME_FULL}.tar.gz" | cut -f1 -d' ')
echo "\""
