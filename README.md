# aruco_generator

## setup

### with nix

```shell
nix shell
```

in case this fails with a complaint about a missing lock file, run:

```shell
nix run .#default.lock
```

then `git add` the newly generated `lock.*.json` file and try again.

### with conda

```shell
conda create -n aruco_generator -c conda-forge python 'opencv>=4.8,<5'
conda activate aruco_generator
pip install .
# or for an editable install: pip install --use-pep517 -e .
```

## run

for example: generate a dictionary of 10 3x3 markers and their images, with size 6cm (using the default 300 ppi), a 1-bit margin (included in the 6cm size), and inverted colors, saving everything into the folder `markers`:

```shell
aruco_generator --num-markers 10 --marker-bits 3 --size-cm 6 --margin-bits 1 --size-includes-margin --invert --output markers
```

see `--help` for more details:

```shell
aruco_generator --help
```
