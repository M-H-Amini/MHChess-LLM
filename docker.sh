#!/bin/bash

docker build -t mh-llm .

docker run -v ${PWD}:/usr/src/app --gpus device=3 --rm -it mh-llm bash -l

