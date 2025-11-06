  pipeline {
    agent any

    environment {
      IMAGE_NAME = "samatoll_back"
      IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    options {
      timestamps()
      ansiColor('xterm')
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
            def cid = sh(script: "docker run -d -e DATABASE_URL=sqlite:\/\/\/\/tmp\/test.db -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}", returnStdout: true).trim()
            try {
              // Wait a bit for the server to start
              sh 'sleep 3'
              // Hit the OpenAPI docs endpoint as a basic liveness check
              sh 'curl -sSf http://localhost:8000/docs >/dev/null'
            } finally {
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


