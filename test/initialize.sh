
source bin/activate
#pip install -r ../../porper-core/src/requirements.txt -t ./lib/python3.6/site-packages
rm -rf ./lib/python3.6/site-packages/porper
cp -r ../../porper-core/porper ./lib/python3.6/site-packages
