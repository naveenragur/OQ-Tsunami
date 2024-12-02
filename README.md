# OpenQuake Engine
A fork of the OpenQuake Engine repository from the official GEM master branch.
Modified to run tsunami risk calculations for my phd work.

# Installation 
Installed the OpenQuake Engine with conda using instructions from:https://rocksandwater.net/blog/2022/11/installing-openquake-with-conda/

# Code changes
To run the OpenQuake Engine, I updated the base.py to override the sitecol check when reading exposure data and ignore the assets not intersecting with the hazards sitcol(latlons).
See read_exposure function in base.py at line 741

