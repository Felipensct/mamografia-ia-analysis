#!/bin/bash
echo "Parando serviços..."
kill 21225 21256 2>/dev/null
echo "Serviços parados!"
