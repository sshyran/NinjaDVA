#!/usr/bin/ruby

require_relative "../config_defaults"
require_relative "html"
require "cgi"
$cgi = CGI.new

h = HTML.new("My Homepage")
h.add_css("codemirror/codemirror.css") # needs to be loaded before other css
h.add_css("myhomepage.css")

if $cgi.include?("url") && $cgi["url"] =~ /\A[\w\-_]*\Z/ && File.exists?("#{$conf.myhomepagedb}/#{$cgi["url"]}.yaml")

	require "yaml"
	homepage = YAML::load_file("#{$conf.myhomepagedb}/#{$cgi["url"]}.yaml")
	if homepage[:password] == $cgi["password"]
		h << "<div>"
		h << "The link to your <a href='#{$cgi["url"]}'>homepage</a>: <input value='http://#{$cgi.server_name}/#{$cgi["url"]}' type='text' readonly='readonly' style='width: 50%' />"

		h << <<EDIT
<form style='height: 100%' method='post' action='store.cgi'>
<div>
<input type='hidden' name='url' value='#{$cgi["url"]}' />
<input type='hidden' name='password' value='#{$cgi["password"]}' />
<textarea id='codeeditor' name='body' style='width: 100%; height:100%'>
#{CGI.escapeHTML(homepage[:html].body)}</textarea>
<input type='submit' value='Save' />
</div>
</form>
</div>
EDIT
h.add_script_file("codemirror/codemirror.js")
h.add_script_file("codemirror/css.js")
h.add_script_file("codemirror/javascript.js")
h.add_script_file("codemirror/vbscript.js")
h.add_script_file("codemirror/xml.js")
h.add_script_file("codemirror/htmlmixed.js")
h.add_script <<JS
  var editor = CodeMirror.fromTextArea(document.getElementById("codeeditor"), {
		mode:  {
			name: "htmlmixed",
			scriptTypes: [
				{matches: /\\/x-handlebars-template|\\/x-mustache/i, mode: null},
        {matches: /(text|application)\\/(x-)?vb(a|script)/i, mode: "vbscript"}
      ]
    },
    lineNumbers: true,
  });
JS

		h << "<h1>Access Log</h1>"
		require "csv"
		fields = ["ADDR","TIME","METHOD","URI","USER_AGENT","REFERER"]
		h << "<table class='requestlog'><tr>#{fields.collect{|e| "<th>#{e}</th>"}.join("")}</tr>"
		CSV.read("#{$conf.myhomepagedb}/#{$cgi["url"]}_access.log",{headers:true}).reverse_each{|log|
			h << "<tr>"
			fields.each{|elem|
				h << "<td>#{log[elem]}</td>"
			}
			h << "</tr>"
		}
		h << "</table>"

	else
		h.header["status"] = "REDIRECT"
		h.header["Cache-Control"] = "no-cache"
		h.header["Location"] = "/?error=#{CGI.escape("Wrong Password for page #{$cgi["url"]}!")}"
	end

else
	h.header["status"] = "REDIRECT"
	h.header["Cache-Control"] = "no-cache"
	h.header["Location"] = "/"
end

h.out($cgi)
