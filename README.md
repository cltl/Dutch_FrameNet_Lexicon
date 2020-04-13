# Dutch FrameNet Lexicon

The goal of this repository is to exploit Dutch resources to create a Dutch FrameNet

### Prerequisites

Python 3.6 was used to create this project. It might work with older versions of Python.

### Installing


#### Python modules

A number of external modules need to be installed, which are listed in **requirements.txt**.
Depending on how you installed Python, you can probably install the requirements using one of following commands:
```bash
pip install -r requirements.txt
```

#### Resources
A number of GitHub repositories need to be cloned. This can be done calling:
```bash
bash install.sh
```

## Contents

### Represent linguistic resources using lib/dfn_classes.FrameNet class
```
cd bash_scripts
bash represent_using_FrameNet_class.sh
```

In the folder **output/output/dfn_objects** you will find:
* combined.p (pickled lib/dfn_classes.FrameNet object)
* graph.p (pickled networkx.classes.graph.Graph object)
* representation.out (std out of representing data using lib/dfn_classes.FrameNet)
* representation.err (std err of representing data using lib/dfn_classes.FrameNet)

### Iteration 1
TODO 

### Annotation
TODO 

### Lexicon data for tool
```
cd bash_scripts
bash lexicon_data_for_tool.sh
```
the folder with the lexicon data for the [annotation tool](https://github.com/cltl/frame-annotation-tool)
is found at **output/lexicon_data_for_frame_annotation_tool**.

## Future work
* incorporate [DutchSemCor](https://github.com/cltl/DutchSemCor_Reader) 
    
## Authors
* **Marten Postma** (m.c.postma@vu.nl)

## License
This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details
