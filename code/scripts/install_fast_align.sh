# Install and build fast_align

git clone https://github.com/clab/fast_align ./../projector/fast_align

echo "Install dependencies"
sudo apt-get install libgoogle-perftools-dev libsparsehash-dev

cd ./../projector/fast_align

echo "Building..."

mkdir build
cd build
cmake ..
make

echo "Completed"