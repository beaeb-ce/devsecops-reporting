def call(Map config = [:]) {
    // Load the Python script
    loadScript(name: 'html_generator.py', path: 'bandit/html_generator.py')
    
    // Load the HTML template
    def tempTemplateFile = 'temp_report_template.html'
    loadScript(name: tempTemplateFile, path: 'bandit/report_template.html')
    
    // Call the Python script with the JSON file and temporary HTML template file
    sh "python ./html_generator.py ${config.json} ${tempTemplateFile}"
}