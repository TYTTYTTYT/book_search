#!/bin/bash
cd /home/tai_yintao101/book_search
screen -S index -dm bash index_server/run.sh
screen -S colbert -dm bash colbert_code/run.sh
screen -S db -dm bash database_code/run.sh
sleep 30
screen -S cache -dm java -jar messageserver-0.0.1-SNAPSHOT.jar