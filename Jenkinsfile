@Library('report-generator') _

// General Configuration
def repoUrl = 'Application_URL'

// Configuration for the "SAST: Trufflehog" stage
def trufflehogRepoBranch = 'CloudGoat'

// Configuration for the "SCA: SonarQube" stage
def sonarProjectKey = 'CloudGoat'
def sonarExclusions = 'TFM/**/*'

pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: python
                    image: python:3
                    command:
                    - cat
                    tty: true
                  - name: docker
                    image: docker:dind
                    securityContext:
                      privileged: true
                    tty: true
                '''
        }
    }  
    
    stages {
        stage('PREREQUIREMENTS') {
            steps {
                container('python') {
                    sh 'python3 --version || echo Python 3 is not installed'
                    echo 'Checking Pip...'
                    sh 'pip --version || echo Pip is not installed'
                }
            }
        }
        
        stage('[TEST]'){
            steps{
                echo '[TEST]'
            }
        }

        stage("SCA: Safety") {
            steps {
                container('docker') {
                    sh '''
                            touch safety-results.json
                            chown 1000:1000 safety-results.json
                            '''
                    sh 'docker run -v "$(pwd)":/src --rm hysnsec/safety check -r requirements.txt --json | tee safety-results.json'
                }
            }
            post {
                always {
                    stash includes: 'safety-results.json', name: 'safety-results'
                }
            }
        }

        stage('SCA: SonarQube') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner1'
                    withSonarQubeEnv {
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=${sonarProjectKey} -Dsonar.exclusions=${sonarExclusions}"
                    }
                    
                    def sonarUrl = 'http://sonarqube-sonarqube.sonarqube.svc.cluster.local:9000'
                    
                    withCredentials([string(credentialsId: '11a29cee-2600-4e76-8179-62a7a8cafffe', variable: 'SONAR_TOKEN')]) {
                        sh """
                            # Retrieve open issues
                            curl -u \$SONAR_TOKEN: -X GET "$sonarUrl/api/issues/search?componentKeys=${sonarProjectKey}&statuses=OPEN" > sonarqube_open_issues.json
                            
                            # Retrieve opened security hotspots
                            curl -u \$SONAR_TOKEN: -X GET "$sonarUrl/api/hotspots/search?projectKey=${sonarProjectKey}&statuses=TO_REVIEW" > sonarqube_open_hotspots.json
                        """
                    }
                }
            }
            post {
                always {
                    stash includes: 'sonarqube_open_issues.json', name: 'sonarqube_open_issues'
                    stash includes: 'sonarqube_open_hotspots.json', name: 'sonarqube_open_hotspots'
                }
            }
        }

        stage("SAST: Trufflehog") {
            steps {
                container('docker') {
                    catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                        git branch: trufflehogRepoBranch,
                        url: repoUrl
                        
                        sh '''
                        touch trufflehog-results.json
                        chown 1000:1000 trufflehog-results.json
                        '''
                        
                        sh '''
                        echo '[' > trufflehog-results.json && \
                        docker run --user 1000:1000 -v "$(pwd)":/src --rm hysnsec/trufflehog file:///src --json | sed 's/}$/},/' | tee -a trufflehog-results.json && \
                        sed -i '$ s/},/}/' trufflehog-results.json && \
                        echo ']' >> trufflehog-results.json '''
                    }
                }
            }
            post {
                always {
                    stash includes: 'trufflehog-results.json', name: 'trufflehog-results'
                }
            }
        }

        stage("SAST: Bandit") {
            steps {
                container('docker') {
                    catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                        sh 'docker run --user 1000:1000 -v "$(pwd)":/src --rm hysnsec/bandit -r /src -f json -o /src/bandit-results.json'
                    }
                }
            }
            post {
                always {
                    stash includes: 'bandit-results.json', name: 'bandit-results'
                }
            }
        }
        

        stage('[REPORTS CREATION]'){
            steps{
                echo '[REPORTS CREATION]'
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                container('python') {
                    sh 'python3 -m venv venv'
                    sh '. venv/bin/activate'
                    script {
                        def requirementsContent = libraryResource('requirements.txt')
                        writeFile file: 'requirements.txt', text: requirementsContent
                        sh 'pip install -r requirements.txt'
                    }
                }
            }
        }

        stage("Report Generation: SonarQube") {
            steps {
                container('python') {
                    script {
                        echo "Activating virtual environment:"
                        sh '. venv/bin/activate'
                        unstash 'sonarqube_open_issues' 
                        unstash 'sonarqube_open_hotspots'

                        generateSonarqubeReport(issues_json: 'sonarqube_open_issues.json', hotspots_json: 'sonarqube_open_hotspots.json')
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'sonarqube/sonarqube-report.html', fingerprint: true
                }
            }
        }

        stage("Report Generation: Safety") {
            steps {
                container('python') {
                    script {
                        echo "Activating virtual environment:"
                        sh '. venv/bin/activate'
                        unstash 'safety-results' 
                        echo "Workspace directory is: ${env.WORKSPACE}"

                        generateSafetyReport(json: 'safety-results.json')
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'safety/safety-report.html', fingerprint: true
                }
            }
        }

        stage("Report Generation: Trufflehog") {
            steps {
                container('python') {
                    script {
                        echo "Activating virtual environment:"
                        sh '. venv/bin/activate'
                        unstash 'trufflehog-results' 
                        echo "Workspace directory is: ${env.WORKSPACE}"

                        generateTrufflehogReport(json: 'trufflehog-results.json')
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trufflehog/trufflehog-report.html', fingerprint: true
                }
            }
        }

        stage("Report Generation: Bandit") {
            steps {
                container('python') {
                    script {
                        echo "Activating virtual environment:"
                        sh '. venv/bin/activate'
                        unstash 'bandit-results' 

                        generateBanditReport(json: 'bandit-results.json')
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit/bandit-report.html', fingerprint: true
                }
            }
        }
        
        stage('[Release]'){
            steps{
                echo '[Release]'
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: '**/*.json', fingerprint: true
            }
        }
        

    }

}
