#!/bin/bash
echo "Parando serviços..."
kill 38937 38966 2>/dev/null
echo "Serviços parados!"
