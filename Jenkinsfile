pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright/python:v1.63.0-noble'
        }
    }

    parameters {
        string(name: 'BASE_URL', defaultValue: '', description: 'URL of the deployed app under test (running with AUTH_DISABLED=true)')
        string(name: 'PYTEST_MARKERS', defaultValue: 'smoke or regression', description: 'Pytest -m marker expression to run')
    }

    stages {
        stage('Validate parameters') {
            steps {
                script {
                    if (!params.BASE_URL?.trim()) {
                        error 'BASE_URL parameter is required'
                    }
                }
            }
        }

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
                // BASE_URL is exposed to the tests as an environment variable (see tests/conftest.py)
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
