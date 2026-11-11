JENKINS ON WINDOWS (with Docker Desktop)
1. Install Docker Desktop (docker.com), restart, open it, wait until it says "Engine running".
2. In PowerShell:  cd case03\jenkins
   docker build -t jenkins-py .
   docker run -d --name jenkins -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins-py
3. Password:  docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
4. Open http://localhost:8080 , paste it, "Install suggested plugins", create an admin user.
5. New Item > name FoodDelivery > Pipeline > OK.
   Pipeline: "Pipeline script from SCM" > Git > your GitHub repo URL > branch */main (or */master)
   Script Path: case03/Jenkinsfile > Save.
6. Build with Parameters: TARGET=fixed  -> green build. Screenshot the stage view and Console Output.
   Build with Parameters: TARGET=original -> red build (tests fail). Screenshot it too.
