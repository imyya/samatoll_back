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
            // Use a temporary SQLite DB so the app can boot
            def cid = sh(script: 'docker run -d -e DATABASE_URL=sqlite:////tmp/test.db -p 8000:8000 ' + "${IMAGE_NAME}:${IMAGE_TAG}", returnStdout: true).trim()
            try {
              // Wait for server to be ready with retries
              def maxRetries = 30
              def retryCount = 0
              def ready = false
              
              while (retryCount < maxRetries && !ready) {
                sleep(time: 2, unit: 'SECONDS')
                def exitCode = sh(script: "curl -sSf http://localhost:8000/docs >/dev/null 2>&1", returnStatus: true)
                if (exitCode == 0) {
                  ready = true
                  echo "Server is ready!"
                } else {
                  retryCount++
                  echo "Waiting for server... (${retryCount}/${maxRetries})"
                }
              }
              
              if (!ready) {
                // Show container logs for debugging
                echo "Server failed to start. Container logs:"
                sh "docker logs ${cid}"
                error("Server did not become ready after ${maxRetries} retries")
              }
              
              // Final health check
              sh 'curl -sSf http://localhost:8000/docs >/dev/null'
            } finally {
              // Show logs before cleanup
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


