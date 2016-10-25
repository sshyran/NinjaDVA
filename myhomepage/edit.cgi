#!/usr/bin/ruby

DB = "../db/myhomepage/"
require_relative "html"
require "cgi"
$cgi = CGI.new

h = HTML.new("My Homepage")
h.add_css("myhomepage.css")

if $cgi.include?("url") && $cgi["url"] =~ /\A[\w\-_]*\Z/ && File.exists?("#{DB}/#{$cgi["url"]}.yaml")

	require "yaml"
	homepage = YAML::load_file("#{DB}/#{$cgi["url"]}.yaml")
	if homepage[:password] == $cgi["password"]
		h << "The link to your <a href='#{$cgi["url"]}'>homepage</a>: <input value='http://#{$cgi.server_name}/#{$cgi["url"]}' type='text' readonly='readonly'>"

		h << <<EDIT
<form style='height: 100%' method='POST' action='store.cgi'>
<input type='hidden' name='url' value='#{$cgi["url"]}' />
<input type='hidden' name='password' value='#{$cgi["password"]}' />
<textarea name='body' style='width: 90%; height:100%'>
#{homepage[:html].body}
</textarea>
<input type='submit' />
</form>
EDIT
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
