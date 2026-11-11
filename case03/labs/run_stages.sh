#!/bin/bash
# Local emulation of the Jenkinsfile stages (no Jenkins server in the sandbox). usage: run_stages.sh <tree> <build#>
T=$1; N=$2; cd $T; ts(){ date +%H:%M:%S; }; FAIL=0
stage(){ echo "[$(ts)] [Pipeline] { ($1)"; }
rm -rf labs_tests; cp -r $LABS/labs_tests labs_tests; rm -f labs_tests/run_tests.sh
echo "Started by GitHub push (emulated)  — Build #$N"
stage Checkout; echo "[$(ts)] > git checkout main  (workspace: $(basename $T))"
stage Build;    echo "[$(ts)] + pip install -r requirements.txt"; pip install -q --dry-run -r requirements.txt >/dev/null 2>&1 && echo "   requirements resolved"
echo "[$(ts)] + python manage.py check"; PYTHONPATH=. python manage.py check 2>&1 | sed 's/^/   /'
echo "[$(ts)] + python manage.py makemigrations --check --dry-run"; PYTHONPATH=. python manage.py makemigrations --check --dry-run 2>&1 | sed 's/^/   /'
stage Test;     echo "[$(ts)] + python manage.py test labs_tests.test_ai10 labs_tests.test_cart_order labs_tests.test_equivalence"
OUT=$(PYTHONPATH=. python manage.py test labs_tests.test_ai10 labs_tests.test_cart_order labs_tests.test_equivalence 2>&1); RC=$?
echo "$OUT" | grep -E "^(FAIL:|ERROR:|Ran|OK|FAILED)" | sed 's/(labs_tests.*//;s/^/   /'
if [ $RC -ne 0 ]; then FAIL=1; echo "ERROR: script returned exit code 1"; echo "[Pipeline] // stage (Test) FAILED"; echo "Stage 'Package' skipped due to earlier failure(s)"; else
 stage Package; echo "[$(ts)] + zip -qr foodmvp-$N.zip config orders restaurants static manage.py requirements.txt Dockerfile docker-compose.yml"; zip -qr /tmp/foodmvp-$N.zip config orders restaurants static manage.py requirements.txt Dockerfile docker-compose.yml 2>/dev/null; echo "   archiveArtifacts: foodmvp-$N.zip ($(du -k /tmp/foodmvp-$N.zip | cut -f1) KB)"; fi
echo "[Pipeline] { (Declarative: Post Actions)"
if [ $FAIL -eq 1 ]; then echo "[Pipeline] mail  -> to: team@example.com | subject: FAILED: FoodDeliveryMVP #$N   (simulated: no SMTP in sandbox)"; echo "Finished: FAILURE"; else echo "Build, tests and package passed - artifact archived."; echo "Finished: SUCCESS"; fi
rm -rf labs_tests; exit $FAIL
