FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install dependencies and add deadsnakes PPA for Python 3.9
RUN apt-get update && apt-get install -y software-properties-common wget \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.9 python3.9-venv python3.9-dev \
    # Install GTK3 and core dependencies
    libgtk-3-dev libcairo2-dev libgirepository1.0-dev \
    # Install packaging tools
    dpkg-dev \
    && rm -rf /var/lib/apt/lists/*

# Set python3 to point to python3.9
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Setup virtualenv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install wheel
RUN pip install --upgrade pip wheel

# Create workspace
WORKDIR /workspace

# Install app dependencies
COPY requirements.txt /workspace/
RUN pip install -r requirements.txt
RUN pip install pyinstaller

# Copy the rest of the application
COPY . /workspace/

# Build C extensions (Swiss Ephemeris)
RUN python3 setup.py build_ext --inplace

# Build the executable with PyInstaller
RUN pyinstaller --noconfirm --clean --windowed --name Astro-Nex nex.py

# Create the .deb package structure
RUN mkdir -p /deb_build/usr/bin \
    && mkdir -p /deb_build/usr/share/fonts/truetype/astronex \
    && mkdir -p /deb_build/usr/share/applications \
    && mkdir -p /deb_build/usr/share/pixmaps \
    && mkdir -p /deb_build/DEBIAN

# Copy binary
RUN cp -r dist/Astro-Nex/* /deb_build/usr/bin/

# Copy font
RUN cp astronex/resources/Astro-Nex.ttf /deb_build/usr/share/fonts/truetype/astronex/

# Copy icon
RUN cp astronex/resources/iconex-beta-256.png /deb_build/usr/share/pixmaps/astronex.png

# Create .desktop file
RUN echo "[Desktop Entry]" > /deb_build/usr/share/applications/astronex.desktop \
    && echo "Name=Astro-Nex" >> /deb_build/usr/share/applications/astronex.desktop \
    && echo "Comment=Astro-Nex Astrology Software" >> /deb_build/usr/share/applications/astronex.desktop \
    && echo "Exec=/usr/bin/Astro-Nex" >> /deb_build/usr/share/applications/astronex.desktop \
    && echo "Icon=astronex" >> /deb_build/usr/share/applications/astronex.desktop \
    && echo "Terminal=false" >> /deb_build/usr/share/applications/astronex.desktop \
    && echo "Type=Application" >> /deb_build/usr/share/applications/astronex.desktop \
    && echo "Categories=Utility;" >> /deb_build/usr/share/applications/astronex.desktop

# Create DEBIAN/control file
RUN echo "Package: astronex" > /deb_build/DEBIAN/control \
    && echo "Version: 2.0" >> /deb_build/DEBIAN/control \
    && echo "Architecture: amd64" >> /deb_build/DEBIAN/control \
    && echo "Maintainer: Isaias <isaias@example.com>" >> /deb_build/DEBIAN/control \
    && echo "Description: Astro-Nex 2.0 Astrology Software" >> /deb_build/DEBIAN/control \
    && echo "Depends: libgtk-3-0" >> /deb_build/DEBIAN/control

# Create postinst script to update font cache
RUN echo "#!/bin/sh" > /deb_build/DEBIAN/postinst \
    && echo "fc-cache -f -v" >> /deb_build/DEBIAN/postinst \
    && chmod 755 /deb_build/DEBIAN/postinst

# Build the .deb
RUN dpkg-deb --build /deb_build /astronex_2.0_amd64.deb

# The entrypoint will be overridden to copy the .deb out
CMD ["/bin/bash"]
