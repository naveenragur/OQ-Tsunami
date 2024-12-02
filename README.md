# OpenQuake Engine
Backup of the OpenQuake Engine repository from official master branch.
Modified to run tsunami risk calculations fo rmy phd work.

# Installation 
Installed the OpenQuake Engine wiht conda using instruction from:https://rocksandwater.net/blog/2022/11/installing-openquake-with-conda/

# Code changes
To run the OpenQuake Engine, I updated the base.py to overide the sitecol check when reading exposure data and ignore the assets not intersecting with the hazards sitcol lat lons.
See read_exposure function in base.py at line 741

