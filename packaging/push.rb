#!/usr/bin/env ruby

token = ENV["TOKEN"]

# el/6/some.rpm or debian/wheezy/some.deb
Dir.glob("*/*/*") do |file|
  distrib, codename, package = file.split("/")
  puts "Push #{package} for #{distrib}/#{codename}..."
  cmd = "package_cloud push postgrespro/mamonsu/#{distrib}/#{codename} #{file}"
  system({'LANG' => 'C.UTF-8', 'PACKAGECLOUD_TOKEN' => token}, cmd)
  exit $?.exitstatus unless $?.success?
end
