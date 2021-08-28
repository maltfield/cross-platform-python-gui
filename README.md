![](https://github.com/maltfield/cross-platform-python-gui/workflows/build/badge.svg)

# Cross Platform Python GUI

This repo is a fork-ready base for your new cross-platform, python-based GUI application.

It includes the CI pipeline to automatically build self-contained executables for Linux (AppImage), Windows (exe), and MacOS (dmg).

This project uses [kivy](https://kivy.org/), which also supports android and iOS--though building apps for these platforms hasn't been automated into GitHub Actions (yet). PRs Welcome! ;)

# How to use this repo

1. Fork this repo
1. On your forked repo, go to the "Actions" tab and click "I understand my workflows, go ahead and enable them" to enable GitHub workflows
1. Edit [src/main.py](/src/main.py) as needed
1. Add any required python modules to [requirements.txt](/requirements.txt)

When you push git commits to github on master, github will automatically spin up containers in the cloud and build your application's executables for all target platforms.

# Demos

## "Hello World" App

Checkout our [Releases Section](https://github.com/maltfield/cross-platform-python-gui/releases) to download and run the self-contained `Hello World` executables for Linux, Windows, and MacOS that were built by this repo.

 * [https://github.com/maltfield/cross-platform-python-gui/releases](https://github.com/maltfield/cross-platform-python-gui/releases)

## In the wild

The following apps have been built by forking this repo

 * [BusKill](https://github.com/buskill/buskill-app)
 * [Kivy Matrix Calculator](https://github.com/maltfield/kivy-matrix-calculator)
 * [Kivy Snake Game](https://github.com/nandanhere/cross-platform-python-gui/)

# License

The contents of this repo are dual-licensed. All code is GPLv3 and all other content is CC-BY-SA.
