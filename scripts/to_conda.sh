#!/bin/bash
# script: to_conda.sh
# ------------------------
# Uploads a package to anaconda cloud, using as recipe a meta.yaml file.
# NOTE: Currently meta.yaml lies in the repository directory.
#
#
# How to install prerequisites:
# $ conda install conda-build anaconda-client -y
#
# Examples:
# $ anaconda login
# $ source to_conda.sh

python_versions=(3.7 3.8 3.9)

mkdir build
cd build

# Build for all specified python versions.
for v in ${python_versions[@]}; do
  conda build --python $v ../../. --no-test
done

# Delete ouput_dir, if it exists, not to accidentally upload stuff.
if [ -d /output_dir ]; then
  rm -rf /output_dir
fi

# Convert the package for all platforms if it is not already a noarch version.
output_tar=$(conda build ../../. --output)
if [[ $output_tar != *"noarch"* ]]; then
  conda convert --platform all $output_tar -o output_dir/

  # Upload platformwise packages to anaconda cloud
  for arch_dir in output_dir/*; do
    for arch_tar in $arch_dir/*.tar.bz2; do
      anaconda upload $arch_tar
    done
  done
fi

# clean the tars created
conda build purge
# Remove the build folder
cd ../
rm -rf build/
echo "The package was successfully uploaded to the anaconda cloud."
