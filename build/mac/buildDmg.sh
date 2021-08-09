#!/bin/bash
set -x
################################################################################
# File:    mac/buildDmg.sh
# Purpose: Builds a self-contained dmg for a simple Hello World
#          GUI app using kivy. See also:
#
#          * https://kivy.org/doc/stable/installation/installation-osx.html
#          * https://kivy.org/doc/stable/guide/packaging-osx.html
#          * https://blog.fossasia.org/deploying-a-kivy-application-with-pyinstaller-for-mac-osx-to-github/
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-06-22
# Updated: 2021-08-09
# Version: 0.3
################################################################################


############
# SETTINGS #
############

PYTHON_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/python3* | sort -n | uniq | head -n1`"
PIP_PATH="`find /usr/local/Cellar/python* -type f -wholename *bin/pip3* | sort -n | uniq | head -n1`"
APP_NAME='helloWorld'

PYTHON_VERSION="`${PYTHON_PATH} --version | cut -d' ' -f2`"
PYTHON_EXEC_VERSION="`echo ${PYTHON_VERSION} | cut -d. -f1-2`"

########
# INFO #
########

# print some info for debugging failed builds
uname -a
sw_vers
which python2
python2 --version
which python3
python3 --version
${PYTHON_PATH} --version
echo $PATH
pwd
ls -lah

###################
# INSTALL DEPENDS #
###################

# first update brew
#  * https://blog.fossasia.org/deploying-a-kivy-application-with-pyinstaller-for-mac-osx-to-github/
#brew update

# install os-level depends
#brew install wget python3
#brew reinstall sdl2 sdl2_image sdl2_ttf sdl2_mixer

brew -v uninstall --ignore-dependencies python
brew -v reinstall build/deps/python-3.7.8.catalina.bottle.tar.gz
PYTHON_PATH="`find /usr/local/Cellar/python -type f -wholename *bin/python3* | sort -n | uniq | head -n1`"

brew reinstall build/deps/sdl2-2.0.12_1.catalina.bottle.tar.gz
brew reinstall build/deps/sdl2_image-2.0.5.catalina.bottle.tar.gz
brew reinstall build/deps/sdl2_mixer-2.0.4.catalina.bottle.tar.gz
brew reinstall build/deps/sdl2_ttf-2.0.15.catalina.bottle.tar.gz

# get python essential dependencies
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/pip-20.1.1-py2.py3-none-any.whl
PIP_PATH="`find /usr/local/Cellar/python -type f -wholename *bin/pip3* | sort -n | uniq | head -n1`"

${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/setuptools-49.1.0-py3-none-any.whl
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/wheel-0.34.2-py2.py3-none-any.whl

# setup a virtualenv to isolate our app's python depends
#sudo ${PYTHON_PATH} -m ensurepip
#${PIP_PATH} install --upgrade --force-reinstall --user pip setuptools
#${PYTHON_PATH} -m pip install --upgrade --user virtualenv
#${PYTHON_PATH} -m virtualenv /tmp/kivy_venv

# install kivy and all other python dependencies with pip
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/Kivy-1.11.1-cp37-cp37m-macosx_10_6_intel.macosx_10_9_intel.macosx_10_9_x86_64.macosx_10_10_intel.macosx_10_10_x86_64.whl
${PIP_PATH} install --ignore-installed --upgrade --cache-dir build/deps/ --no-index --find-links file://`pwd`/build/deps/ build/deps/PyInstaller-3.6.tar.gz

#####################
# PYINSTALLER BUILD #
#####################

mkdir pyinstaller
pushd pyinstaller

cat >> ${APP_NAME}.spec <<EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['../src/main.py'],
             pathex=['./'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='${APP_NAME}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe, Tree('../src/'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='${APP_NAME}')
app = BUNDLE(coll,
             name='${APP_NAME}.app',
             icon=None,
             bundle_identifier=None)
EOF

${PYTHON_PATH} -m PyInstaller -y --clean --windowed "${APP_NAME}.spec"

pushd dist
hdiutil create ./${APP_NAME}.dmg -srcfolder ${APP_NAME}.app -ov
popd

#####################
# PREPARE ARTIFACTS #
#####################

# create the dist dir for our result to be uploaded as an artifact
mkdir -p ../dist
cp "dist/${APP_NAME}.dmg" ../dist/

#######################
# OUTPUT VERSION INFO #
#######################

uname -a
sw_vers
which python2
python2 --version
which python3
python3 --version
${PYTHON_PATH} --version
echo $PATH
pwd
ls -lah
ls -lah dist

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
