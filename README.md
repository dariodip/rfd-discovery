# **rfd-discovery**
###### By
 - [Altamura Antonio](https://www.linkedin.com/in/antonio-altamura-26ab85136/en)
 - [Tomeo Mattia](https://www.linkedin.com/in/mattia-tomeo-b71aa6130/en)
 - [Di Pasquale Dario](https://it.linkedin.com/in/dario-di-pasquale)

## Description
This project, written in Python and Cython, deals with Discovery of Relaxed Functional Dependencies(RFDs)
[[1](http://hdl.handle.net/11386/4658456)] using a bottom-up approach:
instead of giving a fixed threshold on input and discovery all the RDFs, this method infers distances from different RHS
 attributes by itself and then discover the RFDs for these ones.
 
 rfd-discovery takes a dataset, representing a table of a relational database, in CSV format as input and prints the set
 of the discovered RFDs. 
 
 CSV file can contain the following formats:
  - int; <br>
  - int32; <br>
  - int64; <br>
  - float; <br>
  - float64; <br>
  - string; <br>
  - datetime64*. 
  
  *for date format you can use each format known by [pandas](http://pandas.pydata.org/pandas-docs/stable/timeseries.html)
   <br>
  

***Index:***
 - [Requirements](#requirements)
 - [Setup rfd-discovery](#setup)
 - [Build](#build)
 - [Usage](#usage)
 
## Requirements
rfd-discovery is developed using [Python 3.5](http://www.python.it/) and [Cython 0.25.2](http://cython.org/),
 the latter is used to improve time and memory consuming in CPU-bound operations. 
 
 For running rdf-discovery correctly, you have to install **Python 3.5** (or high) and **Cython 0.25** (or high).
 For installing correctly all the requirements you have to install **pip 9.0** (or high).
 
 rdf-discovery use the following Python's libraries:<br>
    *[matplotlib✛](http://matplotlib.org/)*<br>
    *[numpy✛](http://www.numpy.org/)* <br>
    *[pandas✛](http://pandas.pydata.org/)* <br>
    *[tornado](http://www.tornadoweb.org/en/stable/)* <br>
    *[Cython](http://cython.org/)* <br>
    *[nltk](http://www.nltk.org/)* <br>
    *[python-dateutil](https://dateutil.readthedocs.io/en/stable/)* <br>
    *[flask](http://flask.pocoo.org/)* <br>
    
   You can install these one by one, or following the [Setup Section](#setup).

✛these libraries are part of [SciPy stack](https://www.scipy.org/index.html) 
## Setup
In order to install rfd-discovery and all his requirements, run the following:

`python setup.py install`

This should install, using [pip](https://pypi.python.org/pypi/pip), all the [requirements](#requirements). 


## Build

Part of rfd-discovery is written using *Cython*, a superset of the Python programming language, designed to give C-like 
performance with code which is mostly written in Python. This because operations that take place in the code are mostly
CPU bound, wasting computation and memory resources. <br> You can compile Cython code running the following:

`python build.py build_ext --inplace`

this generate C code from Cython code and try to compile it. <br>

** Note that you'll need gcc or other C compiler  **

If building phase ends without errors, you should have some *.c* and *.pyd* (or *.so*, depending by your OS) files. Don't
 worry about dealing with these, Python do it automatically **:)**.


## Usage

Using rdf-discovery is easy enough. Just run the following command:

`python3 main.py -c <csv-file> -r [rhs_index] -l [lhs_indexes] -s [sep] -h [header] -i [index col] 
-d [datetime columns] (--semantic)`

where:
 - *`-c <your-csv>`*: is the path of the dataset on which you want to discover RFDs;
 - *`-s sep`*(optional): is the separation char used in your CSV file. If you don't provide this, rfd-discovery tries to infer
 it for you;
 - *`-h head`*(optional): is the line in which the header of your CSV file is. -1 if your CSV has no header. If you don't 
 provide this, rdf-discovery tries to infer it for you.
 - *`-r rhs_index`*(optional): is the column number of the RHS attribute. It must be a valid integer. You can avoid to 
 specify it only if you don't specify LHS attributes (we'll find RFDs using each attribute as RHS and the remaining as LHS);
 - *`-l lhs_indexes`*(optional): column index of LHS' attributes indexes separated by commas (e.g. *1,2,3*). You can avoid to 
 specify them: <br> 
  if you don't specify RHS' attribute index we'll find RFDs using each attribute as RHS and the remaining as LHS; <br>
  if you specify a valid RHS index we'll assume your LHS as the remaining attributes;
 - *`-i index col`*(optional): the column which contains the primary key of the dataset. Specifying it, this will not 
 calculate as distance. **NOTE: index column should contains unique values**;
 - *`-d datetime columns`*(optional): a list of columns which values are in datetime format. Specifying this, rfd-discovery
 can depict distance between two date in time format (e.g. ms, sec, min);
 - *`--semantic`*(optional): use semantic distance on Wordnet for string. 
 For more info [here.](http://www.cs.toronto.edu/pub/gh/Budanitsky+Hirst-2001.pdf)   
 
 
 ##### Valid Examples:
 ###### Check on each combination of attributes:
  `python main.py -c resources/dataset.csv`
  ###### Infer LHS attributes given a fixed RHS' attribute index:
  `python main.py -c resources/dataset.csv -r 0`
 ###### RHS and LHS fixed, separator and header line specified: 
 `python main.py -c resources/dataset.csv -r 0 -l 1,2,3 -s , -h 0`
