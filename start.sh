#!/bin/bash


a=$(whoami);


if [ $a != "root" ]; then
        echo "Please use sudo" 1>&2 ;
        exit 1;
fi


source ./env/bin/activate ; 
service redis-server start ;
service mongodb start ;
service postgresql start ;


./env/bin/python ApiService.py 2> ./logs/log &
./env/bin/python PreprocessrorService.py 2> ./logs/log &
./env/bin/python ValidatorService.py 2> ./logs/log &
./env/bin/python SessionGeneratorService.py 2> ./logs/log &
./env/bin/python AprioriService.py 2> ./logs/log &

