# CDB_to_INP_converter

Converts the .cdb file that ANSYS creates after running CDWRITE in ANSYS mechanical to an ABAQUS .inp file that can be read by FEBio. 

FEBio can only read a limited number of element types from the .inp file. These include but not limited to C3D8 and S4. Further information can be found [here](https://help.febio.org/FEBioStudio/FEBioStudio_1-5-Section-A.4.html) along with which keywords FEBio recognises from the .inp file.

As of yet this code is only suitable to convert files with a single object that is meshed with a single element type. The element types that are currently supported are [C3D8](https://web.mit.edu/calculix_v2.7/CalculiX/ccx_2.7/doc/ccx/node26.html) (first order, 8 node hexahedral or brick) and [S4](https://web.mit.edu/calculix_v2.7/CalculiX/ccx_2.7/doc/ccx/node37.html) (first order, 4 node quadrilateral shell).

More information about ABAQUS input file element types and codes [here](https://web.mit.edu/calculix_v2.7/CalculiX/ccx_2.7/doc/ccx/node25.html).

# Instructions

To use you can clone the repository with:
``` bash
git clone git@github.com:laurencejeppe/CDB_to_INP_converter.git
```
Then optionally create a virtual environment to install python packages locally and activate it:
``` bash
python -m venv venv
source venv/Scripts/activate
```
Then instal the requirements:
``` bash
pip install -r requirements.txt
```
Then you can open and run the GUI.py file to run the program.