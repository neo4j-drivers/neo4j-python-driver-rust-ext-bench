#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

RES_DIR="results"

echo "###################"
echo "# Setting up venv #"
echo "###################"
# fresh venv
rm -rf venv || true
python3.12 -m venv venv
. venv/bin/activate
pip install -U pip
pip install -Ur requirements.txt
rm ./*.csv || true

echo "############################"
echo "# Benchmarking pure Python #"
echo "############################"
# install the patched driver
pip install neo4j==5.24.0

PYTHONUNBUFFERED=1 python work.py | tee "$RES_DIR/python.csv"


echo "#####################################"
echo "# Benchmarking with Rust Extensions #"
echo "#####################################"
# install the rust extension
pip install neo4j-rust-ext==5.24.0.0

PYTHONUNBUFFERED=1 python work.py | tee "$RES_DIR/rust.csv"

python join_csv.py "$RES_DIR/python.csv" "$RES_DIR/rust.csv" | tee "$RES_DIR/results.csv"

python plot.py "$RES_DIR/results.csv" "$RES_DIR"
