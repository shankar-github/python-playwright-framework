pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.11'
        VENV_PATH = "${WORKSPACE}/venv"
        ENV = 'test'
        API_BASE_URL = 'http://localhost:8080/v1'
        GRAPHQL_ENDPOINT = 'http://localhost:8080/graphql'
        WEB_URL = 'http://localhost:3000'
        GRAPHQL_FETCH_SCHEMA = 'false'
    }

    stages {
        stage('Checkout') { steps { checkout scm } }

        stage('Setup') {
            steps {
                sh '''
                    python${PYTHON_VERSION} -m venv ${VENV_PATH}
                    . ${VENV_PATH}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    playwright install --with-deps
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    pip install flake8 black isort pip-audit
                    flake8 framework tests
                    black --check framework tests
                    isort --check-only framework tests
                    pytest tests/core tests/utils tests/reporting -q
                '''
            }
        }

        stage('Start Mock Servers') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    python tests/mocks/mock_api_server.py &
                    python tests/mocks/mock_web_server.py &
                    python scripts/wait_for_mocks.py
                '''
            }
        }

        stage('API Tests') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    pytest -m api -n auto --reruns 2 --alluredir=reports/allure-results
                '''
            }
        }

        stage('Web Tests') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    pytest -m web -n auto --reruns 2 --alluredir=reports/allure-results
                '''
            }
        }

        stage('Smoke Tests') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    pytest -m "smoke and not smoke_db and not smoke_e2e and not smoke_mobile" -n auto --reruns 2 --alluredir=reports/allure-results
                '''
            }
        }

        stage('Mobile Validation') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    pytest -m mobile --collect-only -q
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
        }
    }
}
