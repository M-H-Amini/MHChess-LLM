#!/bin/bash

docker build -t mh-llm .

docker run -v ${PWD}:/usr/src/app --name mh_llm_container --gpus device=2 -it mh-llm bash -l
