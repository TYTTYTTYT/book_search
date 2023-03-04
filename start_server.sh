#!/bin/bash
cd /home/tai_yintao101/book_search
screen -S index -dm index_server/run.sh
screen -S colbert -dm colbert_code/run.sh
screen -S db -dm database_code/run.sh
screen -S cache -dm message_server/run.sh