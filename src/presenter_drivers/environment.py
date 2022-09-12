from os import getenv

# Possible environments are
# local, dev, qa, prod
ENV = getenv("HAMBONE_ENV", getenv("env", "prod")).lower()
LOGLEVEL = getenv("LOGLEVEL", "NOTSET").upper()
