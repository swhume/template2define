# define_generator.py

## Introduction
The define_generator program takes a Data Definition Specification (DDS) model define-360i.json file as input and generates
the define.xml file based on that metadata. The DDS model captures the metadata needed to generate a Define-XML v2.1 
file. The DDS metadata is loaded by another program currently located in the 
[cdisc-org/360i repo](https://github.com/cdisc-org/360i/tree/main/src/define-xml) and generates a Define-XML v2.1 file.
The define_generator.py program uses odmlib to generate the Define-XML output.

Both this application and create_define_json.py are CLI applications and can be run in sequence to produce a Define-XML 
v2.1 file. Once generated, the Define-XML file can be validated and rendered as HTML using the Define-XML style sheet.

The define_generator.py and create_define_json.py are written in Python and are under active development. They are not 
complete and more features will be added in the near future. The DDS model is still evolving and will continue to 
change.

## Getting Started
To run define_generator.py from the command-line: 

```aiignore
python define_generator.py -t ./data/define-360i.json -d ./data/define-360i.xml
```

The odmlib package must be installed to run define_generator.py. See the 
[odmlib repository](https://github.com/swhume/odmlib) to install the odmlib source code and latest features. 
The odmlib package can also be installed from PyPi with the understanding that it is still in development 
so might not have everything available in the odmlib repository. It can be installed from PyPi using:

```aiignore
pip install odmlib
```

## Limitations
define_generator.py is still under development, and the DDS JSON model continues to evolve, so expect changes.
