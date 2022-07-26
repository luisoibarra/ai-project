# Install and build mgiza

# git clone https://github.com/moses-smt/mgiza/ ./../projector/mgiza

cd ./../projector/mgiza/mgizapp

echo "Building..."

cmake .
make
make install

echo "Completed"