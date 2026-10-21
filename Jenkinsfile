pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright/python:v1.63.0-noble'
        }
    }

    parameters {
        string(name: 'PYTEST_MARKERS', defaultValue: 'smoke or regression', description: 'Pytest -m marker expression to run')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'python3 -m pip install -r requirements.txt'
            }
        }

        stage('Run tests') {
            steps {
                sh 'python3 -m pytest -m "${PYTEST_MARKERS}" --junitxml=reports/junit.xml'
            }
        }
    }

    post {
        always {
            junit 'reports/junit.xml'
            archiveArtifacts artifacts: 'test-results/**', allowEmptyArchive: true
        }
    }
}
