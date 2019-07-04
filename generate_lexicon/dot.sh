cd ..
rm -rf dot

python create_dot_vizualizations.py --graph_path="output/graph_v1.p" --rbn_path="resources/ODWN_Reader/output/orbn.p" --output_folder="dot" --verbose="1" > log/dot.out 2> log/dot.err &
