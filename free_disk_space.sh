#!/usr/bin/env bash
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#
# The Azure provided machines typically have the following disk allocation:
# Total space: 85GB
# Allocated: 67 GB
# Free: 17 GB
# This script frees up 28 GB of disk space by deleting unneeded packages and 
# large directories.
# The Flink end to end tests download and generate more than 17 GB of files,
# causing unpredictable behavior and build failures.
#
echo "=============================================================================="
echo "Freeing up disk space on CI system"
echo "=============================================================================="

echo "Listing 100 largest packages"
dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n | tail -n 100
df -h
echo "Removing large packages"
sudo apt-get remove -y '^ghc-8.*'
sudo apt-get remove -y '^dotnet-.*'
sudo apt-get remove -y '^llvm-.*'
sudo apt-get remove -y 'php.*'
sudo apt-get remove -y azure-cli google-cloud-sdk hhvm google-chrome-stable firefox powershell mono-devel
sudo apt-get autoremove -y
sudo apt-get clean
df -h
echo "Removing large directories"
# deleting 15GB
sudo rm -rf /usr/local/.ghcup
sudo rm -rf /opt/hostedtoolcache/CodeQL
sudo rm -rf /usr/local/lib/android/sdk/ndk
sudo rm -rf /usr/share/dotnet
sudo rm -rf /opt/ghc
sudo rm -rf /usr/local/share/boost

# Additional large packages (from workflow steps)
echo "Removing additional large packages..."
sudo apt-get remove -y \
    microsoft-edge-stable google-chrome-stable firefox \
    temurin-8-jdk temurin-11-jdk temurin-17-jdk temurin-21-jdk temurin-25-jdk \
    powershell kubectl mysql-server-core-8.0 mysql-client-core-8.0 \
    llvm-16-dev llvm-17-dev llvm-18-dev \
    postgresql-16 mecab-ipadic containerd.io podman buildah skopeo \
    || true
sudo apt-get autoremove -y || true

# Surgical /opt cleanup (preserving essential runner directories)
echo "Performing surgical /opt cleanup..."
sudo find /opt -maxdepth 1 -mindepth 1 \
    '!' -path /opt/containerd \
    '!' -path /opt/actionarchivecache \
    '!' -path /opt/runner \
    '!' -path /opt/runner-cache \
    -exec rm -rf '{}' ';' 2>/dev/null || true




# Remaining tool cache cleanup
echo "Removing remaining tool cache..."
if [ -d "/opt/hostedtoolcache" ]; then
    rm -rf /opt/hostedtoolcache || true
fi

# Additional aggressive cleanup (from workflow)
echo "Performing additional cleanup..."

# Remove swap files
sudo swapoff -a || true
sudo rm -f /swapfile || true

# Clean Docker aggressively
echo "🧹 Starting Docker cleanup..."
docker system prune -af --volumes || echo "⚠️ Docker system prune failed"

echo "🗑️ Removing Docker images..."
# Remove images only if they exist
if [ -n "$(docker image ls -aq 2>/dev/null)" ]; then
docker rmi $(docker image ls -aq 2>/dev/null) || echo "⚠️ Docker rmi failed"
else
echo "📦 No Docker images to remove"
fi

echo "📚 Cleaning Docker volumes..."
docker volume prune -f || echo "⚠️ Docker volume prune failed"

echo "🧽 Cleaning system caches..."
sudo apt-get clean || echo "⚠️ apt-get clean failed"
sudo rm -rf /var/lib/apt/lists/* /var/log/* /tmp/* /var/tmp/* || echo "⚠️ System cache cleanup failed"

echo "🗑️ Removing .NET..."
sudo rm -rf /usr/share/dotnet/shared/Microsoft.NETCore.App/*/ || echo "⚠️ .NET removal failed"
sudo rm -rf /usr/share/dotnet/host/fxr/*/ || echo "⚠️ .NET host removal failed"
sudo rm -rf /usr/share/dotnet/sdk/*/NuGetFallbackFolder || echo "⚠️ .NET SDK removal failed"

echo "🗑️ Cleaning GitHub Actions caches..."
sudo rm -rf /home/runner/actions-runner/cached/_diag/* || echo "⚠️ Actions cache cleanup failed"
sudo rm -rf /home/runner/work/_temp/* || echo "⚠️ Work temp cleanup failed"
sudo rm -rf /home/runner/actions-runner/_work/_tool/* || echo "⚠️ Actions tool cache cleanup failed"

echo "🧹 Cleaning language caches..."
npm cache clean --force 2>/dev/null || echo "⚠️ npm cache clean failed"
pip cache purge 2>/dev/null || echo "⚠️ pip cache purge failed"
sudo rm -rf ~/.cache/pip 2>/dev/null || echo "⚠️ pip cache removal failed"

echo "📦 Removing unnecessary packages..."
sudo apt-get remove -y \
php* \
mysql* \
postgresql* \
azure-cli \
gh \
|| echo "⚠️ Package removal failed"
sudo apt-get autoremove -y || echo "⚠️ Autoremove failed"

echo "🍺 Cleaning Homebrew..."
rm -rf /home/linuxbrew/.linuxbrew 2>/dev/null || echo "⚠️ Homebrew cleanup failed"

echo "🗂️ Additional cleanup..."
echo "   Removing Python cache directories (fast)..."
sudo rm -rf /usr/share/man /usr/share/doc /usr/share/info 2>/dev/null || echo "   ⚠️ Docs removal skipped"

echo "   Removing Python cache and bytecode..."
sudo rm -rf /usr/lib/python*/__pycache__ 2>/dev/null || echo "   ⚠️ Python lib cache skipped"
sudo rm -rf /usr/local/lib/python*/__pycache__ 2>/dev/null || echo "   ⚠️ Local Python lib cache skipped"

sudo find /usr/lib/python* -name "*.pyc" -delete 2>/dev/null || echo "   ⚠️ Python bytecode cleanup skipped"

echo "   ✅ Fast additional cleanup completed"

curl -fsSL https://raw.githubusercontent.com/kou/arrow/e49d8ae15583ceff03237571569099a6ad62be32/ci/scripts/util_free_space.sh | bash

echo "Disk space after cleanup:"
df -h
