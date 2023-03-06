#!/bin/bash
cd /home/tai_yintao101/book_search
screen -S index -dm bash index_server/run.sh
screen -S colbert -dm bash colbert_code/run.sh
screen -S db -dm bash database_code/run.sh
