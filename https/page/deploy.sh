#!/usr/bin/env bash

rsync -avog --chown calexandra:www -e ssh . rufus:/home/calexandra/https/page
