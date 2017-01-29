# coding: utf-8
require "sqlite3"
require_relative "config_defaults"

require "argon2"
def argon(pw)
	return Argon2::Password.new(secret: $conf.pepper).create(pw)
end

unless Dir.exists?($conf.dbdir)

chown = []

[
	File.dirname($conf.userdb),
	$conf.chatdb,
	File.dirname($conf.funnypicscsv),
	$conf.myhomepagedb,
	$conf.cloudfiles
].each{|dir|
	Dir.mkdir(dir) unless Dir.exists?(dir)
	chown << dir
}


require "digest"
user = "admin"
realm = "Restricted Area"
File.open("#{$conf.dbdir}/.htdigest","w"){|f|
	f << "#{user}:#{realm}:#{Digest::MD5.hexdigest("#{user}:#{realm}:#{$conf.default_userpw}")}\n"
}


##########################
# Clone Cloud users
clouduserdb = SQLite3::Database.new $conf.clouduserdb

# Create a table
clouduserdb.execute <<-SQL
  create table users (
    id TEXT,
    password TEXT
  );
SQL

# Execute a few inserts
{
	"susi" => [argon($conf.default_userpw)]
}.each do |name,data|
  clouduserdb.execute "insert into users VALUES ( ?, ? )", [name] + data
end
chown << $conf.clouduserdb

File.open($conf.cloudfiles+"/Wichtig-unbedingt-lesen-README","w") {|f|
	f << "Diese Cloud hat keinen Virenschutz!"
}

##############################
# Mail users
userdb = SQLite3::Database.new $conf.userdb

# Create a table
userdb.execute <<-SQL
  create table users (
  	id TEXT,
    name TEXT,
    password TEXT,
    message TEXT,
    groups TEXT
  );
SQL

# Execute a few inserts
{
"alice"   => ["Alice Wonder",   Digest::MD5.hexdigest("Password1"), "Follow the white Rabbit", "Newbie"],
"bob"     => ["Bob Builder",    Digest::MD5.hexdigest("Password1"), "Yes we can", "Newbie"],
"wolle"   => ["Wolfgang S.",    Digest::MD5.hexdigest("Gewinner"), "Das muss alles sicherer werden!", "Sicherheitsverantwortlich"],
"admin"   => ["Andi Admin",     argon($conf.default_userpw), "Leave me alone if you don't want to have trouble.", "Administrator, Checker"],
"siggi"   => ["Siggi Sorglos",  argon($conf.default_userpw), "Die Welt ist schön!", "Dummies"],
"mueller" => ["Fräulein Müller-Wachtendonk", argon("Siggi4ever"), "", "Dummies"],
"susi"    => ["Susi Sorglos",   argon($conf.default_userpw), "❤ Otto ❤", "Dummies"],
"heidi"   => ["Heidi Heimlich", argon($conf.default_userpw), "Bitte keine Werbung.", "Support, Hidden"],
"xaver"   => ["Xaver Schmidt",  argon($conf.default_userpw), "Ask me, I will give you support!", "Support"]
}.each do |name,data|
  userdb.execute "insert into users VALUES ( ?, ?, ?, ?, ? )", [name] + data
end
chown << $conf.userdb



maildb = SQLite3::Database.new $conf.maildb

# Create a table
maildb.execute <<-SQL
  create table mail (
  	sender TEXT,
    recipient TEXT,
    subject TEXT,
    body TEXT,
    challenge TEXT
  );
SQL
[
	["Siggi Sorglos",              "group:Administrator","Backdoor Password for all Clients", 
	'Dear Colleagues

Please do not forget our local administrator password which is valid for
all our Windows client computers: "Start123"

Best, Siggi','csrf'],
	["Siggi Sorglos",              "xaver","Grillen",
"Hallo Xaver Sebastian,

bleibts beim Grillen heute Abend?

Ciao, Siggi","xss"],
	["Fräulein Müller-Wachtendonk","siggi","Der Mensch macht's!",
	"Sehr geehrter Herr Sorglos,

vielen Dank für die vielen schönen Produktionen. Ich hoffe Sie denken
immer an unseren gemeinsamen Leitsatz:

Der Mensch macht's!

Viele Grüße,
Müller-Wachtendonk" ,"session_fixation"],
	["Fön",                        "susi", "Küss mich, ich bin ein verzauberter Königssohn!",
"Hallo Susi, ich bin es, dein Fön…

…und ich liebe dein goldenes Haar…","jsonp"]

].each do |data|
  maildb.execute "insert into mail VALUES ( ?, ?, ?, ?, ? )", data
end

chown << $conf.maildb



##### funny-pics
File.open($conf.funnypicscsv, "w"){|f|
	f.puts '"sid","url"'
	f.puts '"example","https://cdn.meme.am/instances/250x/64647060.jpg"'
	f.puts '"example","http://cdn.meme.am/instances/250x/41586830.jpg"'
	f.puts '"example","http://i.imgur.com/4lC3Aur.jpg"'
}
File.open($conf.funnypicsdeletecsv, "w"){|f|
	f.puts '"sid","url"'
}

chown << $conf.funnypicscsv
chown << $conf.funnypicsdeletecsv

File.open($conf.solutiondb, "w"){|f|
	f.puts 'challenge,ip,state,comment,time'
}
chown << $conf.solutiondb


require "fileutils"
FileUtils.chown("www-data","www-data", chown, :verbose => true)
puts "chown www-data:www-data #{chown.join(" ")}"

else
	puts "Directory #{$conf.db} already exists... only changing symlinks"
end

[
	[$conf.cloudfiles,"#{INSTALLDIR}/clonecloud/files"],
	[$conf.dbdir,"#{INSTALLDIR}/db"]
].each{|a,b|
	File.unlink(b)
	File.symlink(a,b)
}
