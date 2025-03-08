#!/bin/bash
curl -o python.tar.gz https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
tar -xzf python.tar.gz
cd Python-3.9.16
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall
cd ..
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt 