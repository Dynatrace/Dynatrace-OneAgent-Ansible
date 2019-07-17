#!/bin/bash

sudo yum install -y \
  bash \
  bzip2 \
  coreutils \
  diffutils \
  dkms \
  gcc  \
  git \
  kernel-devel \
  kernel-headers \
  make \
  mlocate \
  net-tools \
  patch \
  perl \
  policycoreutils-python \
  python \
  rpm-build \
  rpm-devel \
  rpmdevtools \
  rpmlint \
  tree \
  vim-enhanced \
  wget \
  zsh

sudo yum update -y

sudo rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

#install IUS, which stands for Inline with Upstream Stable. A community project, IUS provides Red Hat Package Manager (RPM) packages for some newer versions of select software

sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
sudo yum -y install python36u

sudo yum -y install python36u-pip \
  python36u-devel

# Install Ansible
#sudo yum install -y ansible

# Get oh my zsh its what the cool kids are using
sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

# Set shell to zsh
sudo -s 'echo /usr/local/bin/zsh >> /etc/shells' && chsh -s /usr/local/bin/zsh
sudo -s 'echo "KERN_DIR=/usr/src/kernels/`uname -r`"' >> ~/.zshrc
# Our zsh theme
sudo updatedb
ZSHFILE=`sudo locate '.zshrc'`
sudo sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="ys/g' $ZSHFILE

curl -o /usr/local/bin/rmate https://raw.githubusercontent.com/aurora/rmate/master/rmate
sudo chmod u+x /usr/local/bin/rmate
sudo mv /usr/local/bin/rmate /usr/local/bin/atom

sudo wget http://download.virtualbox.org/virtualbox/4.3.12/VBoxGuestAdditions_4.3.12.iso
sudo mkdir /media/iso
sudo mount -o loop ./VBoxGuestAdditions_4.3.12.iso /media/iso
sudo bash /media/iso/VBoxLinuxAdditions.run --nox11
sudo umount /media/iso

sudo chmod u+x /vagrant/utils/*.sh
