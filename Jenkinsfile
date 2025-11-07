  pipeline {
    agent any

    environment {
      IMAGE_NAME = "samatoll_back"
      IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    options {
      timestamps()
    }

    stages {
      stage('Checkout') {
        steps {
          checkout scm
        }
      }

      stage('Build Docker Image') {
        steps {
          sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
        }
      }

        stage('Smoke Test') {
          steps {
            script {
              def cid = sh(script: 'docker run -d -e DATABASE_URL=sqlite:////tmp/test.db -p 8000:8000 ' + "${IMAGE_NAME}:${IMAGE_TAG}", returnStdout: true).trim()
              def containerIp = sh(
              script: "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${cid}",
              returnStdout: true).trim()
              echo "Container ID: ${cid}"
              echo "Container IP: ${containerIp}"
              try {
                def maxRetries = 30
                def retryCount = 0
                def ready = false
                
                while (retryCount < maxRetries && !ready) {
                  sleep(time: 2, unit: 'SECONDS')
                  def exitCode = sh(script: "curl -sSf http://${containerIp}:8000/health >/dev/null 2>&1", returnStatus: true)
                  if (exitCode == 0) {
                    ready = true
                    echo "Server is ready on http://${containerIp}:8000/health!"
                  } else {
                    retryCount++
                    echo "Waiting for server on /health ... (${retryCount}/${maxRetries})"
                  }
                }
                
                if (!ready) {
                  echo "Server failed to start on Health aget ${maxRetries}. Container logs:"
                  sh "docker logs ${cid}"
                  error("Server did not become ready after ${maxRetries} retries")
                }
                
                sh "curl -sSf http://${containerIp}:8000/health >/dev/null"
              } finally {
                sh "docker logs ${cid} || true"
                sh "docker rm -f ${cid} || true"
              }
            }
          }
        }
      }

    post {
      always {
        sh 'docker image ls ${IMAGE_NAME}:${IMAGE_TAG} || true'
      }
      success {
        echo "Build ${env.BUILD_NUMBER} completed for ${env.JOB_NAME}"
      }
      failure {
        echo "Build failed. Check logs above."
      }
    }
  }


