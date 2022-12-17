#!/bin/bash
COOKIES_FILE=adventofcode.com_cookies.txt
wget --load-cookies=$COOKIES_FILE https://adventofcode.com/2022/day/$1/input -O input/$1.txt
