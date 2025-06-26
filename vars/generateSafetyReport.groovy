
def call(Map config = [:]) {
    // Load the Python script for Safety report generation
    loadScript(name: 'html_generator.py', path: 'safety/html_generator.py')
    
    // Load the HTML template for Safety report
    def tempTemplateFile = 'temp_report_template.html'
    loadScript(name: tempTemplateFile, path: 'safety/report_template.html')
    
    // Call the Python script with the JSON file and temporary HTML template file
    sh "python ./html_generator.py ${config.json} ${tempTemplateFile}"
}