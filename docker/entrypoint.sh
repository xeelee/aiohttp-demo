#!/usr/bin/env bash
EGGDIR="aiohttp_demo.egg-info"

if [ -d "$EGGDIR" ]; then
    rm -rf "${EGGDIR}"
fi

echo 'Installing requirements'
pip install -r requirements.txt.lock
pip install -r requirements_dev.txt
echo 'Done'
python setup.py develop

"$@"
