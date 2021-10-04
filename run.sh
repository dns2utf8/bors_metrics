#!/usr/bin/env bash
set -e

echo `dirname $0`
cd `dirname $0`
echo `pwd`

source venv/bin/activate

set -ex
./fetch_bors_metrics.py 
