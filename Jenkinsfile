pipeline {
    agent {
        label 'slave1'
    }
    stages {
        stage('Build') {
            steps {
                sh 'rm  -f dist/*.gz'
                sh 'rm  -f dist/*.whl'
                sh 'python3 setup_lessons.py -q bdist_wheel'
                sh 'python3 setup_lessons.py -q sdist'
                archiveArtifacts artifacts: 'dist/*.whl', fingerprint: true
                archiveArtifacts artifacts: 'dist/*.tar.gz', fingerprint: true
            }
        }
        stage('Upload') {
            steps {
                withAWS(region:'us-east-1',credentials:'s3-builds') {
                    // Upload files from working directory 'dist' in your project workspace
                    s3Upload(bucket:"builds-dgl", file:'dist', path: 'webapp/bdist');
                }
            }
        }
    }
}
