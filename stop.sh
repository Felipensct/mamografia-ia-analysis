#!/bin/bash
echo "Parando serviços..."
kill 45312 45341 2>/dev/null
echo "Serviços parados!"
