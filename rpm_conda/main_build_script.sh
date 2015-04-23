#
# Note:  This script is just a copy of the one used in Jenkins.  This isn't meant to be run outside of jenkins
#
#!/bin/bash
VERSION="2.2.0"
MINICONDA_VERSION="3.9.1"

# this is usually supplied by Jenkins
BUILD_NUMBER=1

base_url="http://09c8d0b2229f813c1b93-c95ac804525aac4b6dba79b00b39d1d3.r79.cf1.rackcdn.com"
#base_url="http://filer.atx.continuum.io/released/${VERSION}"
link="Anaconda-${VERSION}-Linux-x86_64.sh"
url="${base_url}/${link}"


#miniconda_base_url="http://filer.atx.continuum.io/miniconda"
miniconda_base_url="http://repo.continuum.io/miniconda"
miniconda_link="Miniconda-${MINICONDA_VERSION}-Linux-x86_64.sh"
miniconda_url="${miniconda_base_url}/${miniconda_link}"

# Remove version info from link so post_install scripts don't change with each version
anaconda_installer="Anaconda-Linux-x86_64.sh"
miniconda_installer="Miniconda-Linux-x86_64.sh"

install_dir=install_dir

rm -rf ${install_dir} || /bin/true
mkdir -p ${install_dir}/var/lib/anaconda

# Create Anaconda RPM
echo "Downloading ${url}"
if [[ ! -e ${link} ]] 
then
    wget --quiet ${url}
fi

SCRIPTS="."
cp ${link} "${install_dir}/var/lib/anaconda/${anaconda_installer}"

/usr/bin/fpm -s dir -t rpm -n continuum-anaconda -v ${VERSION} --iteration ${BUILD_NUMBER} -a x86_64 --vendor "Continuum Analytics" --post-install ${SCRIPTS}/post_install.sh --pre-uninstall ${SCRIPTS}/post_remove.sh  -C ${install_dir} var/lib/anaconda 

/usr/bin/fpm -s dir -t deb -n continuum-anaconda -v ${VERSION} --iteration ${BUILD_NUMBER} -a x86_64 --vendor "Continuum Analytics" -d bzip2 --post-install ${SCRIPTS}/post_install.sh --pre-uninstall ${SCRIPTS}/post_remove.sh  -C ${install_dir} var/lib/anaconda 

#### Miniconda
# clear out install dir
rm -rf ${install_dir}
mkdir -p ${install_dir}/var/lib/anaconda

# Create Anaconda RPM
echo "Downloading ${miniconda_url}"
wget --quiet ${miniconda_url}
cp ${miniconda_link} "${install_dir}/var/lib/anaconda/${miniconda_installer}"

/usr/bin/fpm -s dir -t rpm -n continuum-miniconda -v ${MINICONDA_VERSION} --iteration ${BUILD_NUMBER} -a x86_64 --vendor "Continuum Analytics" --post-install ${SCRIPTS}/post_install.sh --pre-uninstall ${SCRIPTS}/post_remove.sh  -C ${install_dir} var/lib/anaconda 

/usr/bin/fpm -s dir -t deb -n continuum-miniconda -v ${MINICONDA_VERSION} --iteration ${BUILD_NUMBER} -a x86_64 --vendor "Continuum Analytics" -d bzip2 --post-install ${SCRIPTS}/post_install.sh --pre-uninstall ${SCRIPTS}/post_remove.sh  -C ${install_dir} var/lib/anaconda 
