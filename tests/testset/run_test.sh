#!/bin/sh

rm -r output
rm trial.png

python ../../submaker.py ./ --trial -v
python ../../submaker.py ./ -v
