#!/bin/bash

# docker build -t mh-llm .

docker run -v ${PWD}:/usr/src/app --gpus device=2 -it mh-llm bash -l
