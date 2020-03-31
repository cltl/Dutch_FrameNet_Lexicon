export output=../output/dfn_objects
mkdir -p $output 

cd ../lib 
python combine_resources.py --config_path="../input/config_files/v0.json" --output_folder=$output --use_cache="False" --verbose=1 > $output/representation.out 2> $output/representation.err &

