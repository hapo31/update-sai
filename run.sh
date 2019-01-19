#!/bin/bash

docker run -d -v $(pwd)/db:/var/scripts/db update_sai
