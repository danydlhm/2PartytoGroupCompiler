# 2PartytoGroupCompiler

## Description

This project is the implementation of the protocol which is defined in the paper “(Password) Authenticated Key Establishment: From 2-Party to Group”. From a high point of view, the protocol initializes a common secret among a group using as tools an AKE 2-party and a Commitment Scheme.

In the actual version (1.0.0), only one tool of each type is coded. The AKE 2-party selected is a Diffie-Hellman exchange key and Cramer-Shoup is selected as commitment Scheme.

The project has two types of execution, **basic** and **realistic**:

* __Basic simulation__: executes all participants in a single process

![basic simulation scheme](https://raw.githubusercontent.com/danydlhm/2PartytoGroupCompiler/master/extras/documentacion/imagenes/Simulacion_basica.png)

* __Realistic simulation__: the main process create a broadcast server and for each participant creates a process that simulate user's behavior.

![realistic simulation scheme](https://raw.githubusercontent.com/danydlhm/2PartytoGroupCompiler/master/extras/documentacion/imagenes/Simulacion_realista.png)

## Installation

The coded are not in PyPi repository, so if you want to install it, you need to download the project from github and install it using the python's setuptools module. The steps are the followings:

```commandline
cd .../2PartytoGroupCompiler
```

```commandline
python setup.py install
```

## Run

The module can be exceuted by the following command:

``` commandline
python -m partygroupcomp [-m=True] [-i={int}]
```

Where the parameters m and i are optionals:

- -m=True: activate the realistic simulation. If the parameter is not included, the process execute the basic simulation
- -i={int}: integer that indicates how many time the protocol are executed for timing measure

