# Install and build mgiza

git clone https://github.com/moses-smt/mgiza/ ./../aligner/mgiza

cd ./../aligner/mgiza/mgizapp

echo "Building..."

cmake .
make
make install

echo "Completed"