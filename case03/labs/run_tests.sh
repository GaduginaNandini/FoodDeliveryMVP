#!/bin/bash
# usage: run_tests.sh <app_dir> <module> [label]
APP=$1; MOD=$2
rm -rf $APP/labs_tests; cp -r "$(dirname "$0")" $APP/labs_tests; rm -f $APP/labs_tests/run_tests.sh
cd $APP && PYTHONPATH=. python manage.py test labs_tests.$MOD -v 2 2>&1 | grep -v -E "^(Operations|  Apply|  Synchron|Creating|Destroying|Found|System check|Running|Using existing)"
rm -rf $APP/labs_tests
