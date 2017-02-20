# RPi home environmental monitoring
## Introduction

This documents a home environmental monitoring project using Raspberry Pis and
anything else that fits.

## Documentation

In the `docs` directory you will find a `requirements.txt` and Sphinx
documentation. To install you will likely want to create a Python virtualenv,
activate it and then:

``` bash
    > pip install -r requirements.txt
    > make html
```

Documentation will be in `build/html/index.html`

## Code

Currently we have only the power monitor code. This is in `src/`. Installation
is currently manual until we've done a little more work. To install:

* Copy the code to your RPi
* Create a virtual environment
* pip install `src/requirements.txt`
* Symlink `/usr/local/rpienv` to the directory containing your virtualenv
* Symlink `/usr/local/rpienv/rpienv` to the `src` directory
* Run `install_init_script.sh` to install the init script which ensures that
  the power monitor starts on boot.

Before you can run the code, copy `settings.py.example` to `settings.py` and
put in appropriate keys, usernames and addresses.

You can run `power.py` from the console. To get help:

``` bash
  > ./power.py -h
```

To run the power monitor without daemonising:

``` bash
  > ./power.py --nodaemon
```

Output will appear in /tmp and in your Librato and InfluxDB databases.
