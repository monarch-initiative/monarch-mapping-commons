pipeline {
    agent { label 'monarch-agent-medium' }
        environment {
        HOME = "${env.WORKSPACE}"
        RELEASE = sh(script: "echo `date +%Y-%m-%d`", returnStdout: true).trim()
        PATH = "/opt/poetry/bin:${env.PATH}"
    }
    stages {
        stage('setup') {
            steps {
                sh 'poetry install'
            }
        }
        stage('download') {
            steps {
                sh '''
                poetry run gene-mapping download
                ls -lasd
                ls -la data

                # Copy the data to the GCP bucket
                gsutil cp data/* gs://monarch-archive/mapping-data-cache/${RELEASE}/
                '''
            }
        }
        stage('generate-mapping-files') {
            steps {
                sh 'make mappings'
            }
        }
        stage('upload-mapping-files'){
            steps{
                sh '''
                    gsutil cp mappings/*.sssom.tsv gs://monarch-archive/mappings/${RELEASE}/
                    gsutil cp mappings/*.sssom.tsv gs://data-public-monarchinitiative/mappings/${RELEASE}/

                    gsutil rm -f gs://data-public-monarchinitiative/mappings/latest/*
                    gsutil cp gs://data-public-monarchinitiative/mappings/${RELEASE}/* gs://data-public-monarchinitiative/mappings/latest/
                '''
            }
        }
        stage('index') {
            steps {
                sh '''
                    echo "Current directory: $(pwd)"
                    python3 --version
                    pip --version
                    export PATH=$HOME/.local/bin:$PATH
                    echo "Path: $PATH"

                    cd $HOME
                    mkdir data-public
                    gcsfuse --implicit-dirs data-public-monarchinitiative data-public

                    git clone https://github.com/monarch-initiative/monarch-file-server.git
                    pip install -r monarch-file-server/scripts/requirements.txt
                    python3 monarch-file-server/scripts/directory_indexer.py --inject monarch-file-server/scripts/directory-index-template.html --directory data-public --prefix https://data.monarchinitiative.org -x
                '''
            }
        }
    }
}
