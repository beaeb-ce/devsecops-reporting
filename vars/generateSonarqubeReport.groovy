def call(Map config = [:]) {
    // Load the Python script
    loadScript(name: 'html_generator.py', path: 'sonarqube/html_generator.py')
    
    // Load the HTML template
    def tempTemplateFile = 'temp_report_template.html'
    loadScript(name: tempTemplateFile, path: 'sonarqube/report_template.html')
    
    // Call the Python script with the JSON files and temporary HTML template file paths
    sh "python ./html_generator.py ${config.issues_json} ${config.hotspots_json} ${tempTemplateFile}"
}
