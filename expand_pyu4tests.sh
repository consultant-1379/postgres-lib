#!/bin/bash
set -x
TARGET_DIR="$(pwd)/target"
cd ${TARGET_DIR}
mkdir pyu4tests
cd pyu4tests
for i in ../*rpm ; do rpm2cpio $i | cpio -idmv ; done
rm -rf opt
cd ..
rm -f *.rpm
