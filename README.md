# pre-processing pipeline
This repository describes an Electronic Medical Record pre-processing pipeline developed at the VU University Amsterdam. The accompanying project has finished for now, and the code is stable. However, we often investigate optimizations and specific segments of the pipeline, as well as potential new ones. These are only added to this repository if we're confident about the performance. Two of those side projects are located [here](https://gitlab.com/crc-project/vumc-crc) and [here](git@gitlab.com:crc-project/patient-clustering.git). Note that these are under active development.

# usage
traverse to the directory, type "python main.py" in your terminal, and the program will boot. 

# issues and contributions
Both are welcome. Submit an issue and assign yourself to it, then I will take any pull request into consideration.

# dependencies
* Python 2.7
 
I recommend downloading the [Anaconda Python distribution](https://docs.continuum.io/anaconda/install) which comes pre-installed with most of the modules below.

Required Python modules:
* numpy
* scipy
* scikit-learn 
* matplotlib
* [cx_Oracle](https://pypi.python.org/pypi/cx_Oracle) (for DB connection). This might be a bit tricky to install but you can get started (here)[https://blogs.oracle.com/opal/entry/configuring_python_cx_oracle_and] and (here)[http://stackoverflow.com/questions/30928203/cx-oracle-does-not-recognize-location-of-oracle-software-installation-for-instal].
* SPARQLWrapper (for the semantic enrichment)
* TKinter / ttk (for the UI)
