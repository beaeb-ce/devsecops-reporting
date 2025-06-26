def call(Map config = [:]) {
  def scriptContents = libraryResource(config.path)
  writeFile file: config.name, text: scriptContents
  sh "chmod a+x ./${config.name}"
}