#!/bin/bash

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/tai_yintao101/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/tai_yintao101/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/tai_yintao101/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/tai_yintao101/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

conda activate ttds
python index_server/index_server.py