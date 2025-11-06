#!/bin/bash
echo "Parando serviços..."
kill 31391 31473 2>/dev/null
echo "Serviços parados!"
