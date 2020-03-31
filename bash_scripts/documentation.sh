#!/usr/bin/env bash

cd ..
pyreverse dfn_classes.py
dot -Tpdf classes.dot -o documentation/dfn_classes.pdf
rm classes.dot