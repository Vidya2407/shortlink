pipeline {
    agent any
    stages {
        stage('Install') {
            steps {
                sh 'python3 -m venv --system-site-packages venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh '. venv/bin/activate && pytest -v'
            }
        }
    }
}