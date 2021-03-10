#!/bin/sh

sigint_handler()
{
  kill $PID
  exit
}

trap sigint_handler SIGINT

while true; do
    $@ &
    PID=$!
    echo "Started process [$PID] $@, waiting for changes in $PWD"
    inotifywait -e modify -e move -e create -e delete -e attrib -r `pwd`
    kill $PID
    echo "Process killed, restarting..."
done