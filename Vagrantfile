Vagrant.configure("2") do |config|
  config.vm.define "centos", primary: true do |centos|
    centos.vm.provision "shell", path: "yum-apt-startup.sh"
    centos.vm.box = "centos/7"
    centos.vm.hostname = 'centos'

    centos.vm.network :private_network, ip: "192.168.56.101"
    centos.vm.network :forwarded_port, guest: 22, host: 10101, id: "ssh"
    centos.vm.network :forwarded_port, guest: 9999, host: 10102, id: "dt"
    centos.vm.network :forwarded_port, guest: 52698, host: 10103, id: "atom"

    centos.vm.provider :virtualbox do |v|
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 512]
    end
  end
end
