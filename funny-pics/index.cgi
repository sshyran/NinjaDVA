#!/usr/bin/ruby

PICS="../db/funny-pics/pics.csv"
DELETE="../db/funny-pics/delete.csv"

require_relative "html"
require "csv"
require "cgi"
require 'cgi/session'
$cgi = CGI.new
$session = CGI::Session.new($cgi)

numpics = $cgi.include?("num") ? $cgi["num"].to_i : 10

h = HTML.new("Funny Pics")

if $cgi.include?("refresh")
	time = $cgi["refresh"].to_i == 0 ? 60 : $cgi["refresh"].to_i
	h.add_html_head("<meta http-equiv='refresh' content='#{time}'>")
end

h << <<CONTENT
<div>
<form method="POST">
<div style='float:right'>
	Show only last:
CONTENT
[5,10,15,20,25].each{|i|
	if numpics == i
		h << i.to_s
	else
		h << "<a href='?num=#{i}' />#{i}</a>"
	end
}
h << <<CONTENT
</div>
This Picture URL is really funny:
	<input type='text' style='width: 100%' name='pic_url' placeholder='http://...'/>
	<input type='submit'/>
</form>
</div>
CONTENT


if $cgi.include?("pic_url")
	if $cgi["pic_url"] =~ /^https?:\/\//
		File.open(PICS, 'a') { |f|
			f << [$session.session_id,$cgi["pic_url"]].to_csv
		}

		#################
		# CSRF
		MAILSERVER = "http://mail.mgmsp-lab.com"
		if $cgi["pic_url"].start_with?(MAILSERVER)
			require "sqlite3"
			USERDB = "../db/users.db"
			userdb = SQLite3::Database.new(USERDB)
			userid = "admin"
			pass = userdb.get_first_row("SELECT password FROM users WHERE id = ?",userid)[0]
			cookiefile = `mktemp`.chomp
			CURL = "curl --stderr /dev/null -o /dev/null --cookie-jar '#{cookiefile}' --cookie '#{cookiefile}'"

			`#{CURL} '#{MAILSERVER}/'`
			`#{CURL} '#{MAILSERVER}/login.cgi' -H 'Content-Type: application/x-www-form-urlencoded' --data "username=#{userid}&password=#{pass}"`
			`#{CURL} "#{$cgi["pic_url"].gsub('"','\"')}" -L`
			`#{CURL} '#{MAILSERVER}/logout.cgi'`
			`rm #{cookiefile}`
		end
		#################
	else
		h << "<div style='color: red'>URL should start with http</div>"
	end
end
if $cgi.include?("delete")
	File.open(DELETE, 'a') { |f|
		f << [$session.session_id,$cgi["delete"]].to_csv
	}
end

h << "<div style='margin:10px'>"
pics = CSV.read(PICS,{headers: true, col_sep: ","})
del = CSV.read(DELETE,{headers: true, col_sep: ","}).to_a

pics_to_use = []
pics.reverse_each{|l|
		unless del.include?([l["sid"],l["url"]])
			if (!(l["url"] =~ /^https?:\/\/.*\.mgmsp-lab\.com\// || l["url"] =~ /^https?:\/\/172\.23\.42\.[0-9]{1,3}\//)) ||
					l["sid"] == $session.session_id ||
					$cgi.include?("all_pics")
				pics_to_use << l
			end
		end
}

pics_to_use[0..(numpics-1)].each{|l|
	h << "<div style='display: inline-block; min-width: 10em'>"
	if l["sid"] == $session.session_id
		h << "<div style='position: absolute;'>"
		h << "<form method='POST'>"
		h << "<input type='submit' value='Delete' />"
		h << "<input type='hidden' name='delete' value=\"#{CGI.escapeHTML(l["url"])}\" />"
		h << "</form></div>"
	end
	h << "<img src='#{CGI.escapeHTML(l["url"])}' height='250px' />"
	h << "</div>"
}

h << "</div>"

h.out($cgi)
