FROM python:3.9-slim-buster

ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Fix apt sources since Buster is EOL and moved to archive
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list \
    && sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list \
    && sed -i '/buster-updates/d' /etc/apt/sources.list

# Install dependencies (Python 3.9 is already included in this image)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgtk-3-dev libcairo2-dev libgirepository1.0-dev \
    dpkg-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
RUN pip install --upgrade pip wheel

# Create workspace
WORKDIR /workspace

# Install app dependencies
RUN pip install pytz configobj Pillow ipython pyinstaller

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

# Copy missing data folders (resources, db, locale) that PyInstaller missed
RUN mkdir -p /deb_build/usr/bin/astronex \
    && cp -r astronex/resources /deb_build/usr/bin/astronex/ \
    && cp -r astronex/db /deb_build/usr/bin/astronex/ \
    && cp -r astronex/locale /deb_build/usr/bin/astronex/

# Copy font
RUN cp astronex/resources/Astro-Nex.ttf /deb_build/usr/share/fonts/truetype/astronex/

# Copy icon
RUN cp astronex/resources/iconex-beta-48.png /deb_build/usr/share/pixmaps/astronex.png

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
    && echo "Depends: libgtk-3-0, python3-gi, python3-gi-cairo, gir1.2-gtk-3.0" >> /deb_build/DEBIAN/control

# Create postinst script to update font cache
RUN echo "#!/bin/sh" > /deb_build/DEBIAN/postinst \
    && echo "fc-cache -f -v" >> /deb_build/DEBIAN/postinst \
    && chmod 755 /deb_build/DEBIAN/postinst

# Build the .deb
RUN dpkg-deb --build /deb_build /astronex_2.0_amd64.deb

# The entrypoint will be overridden to copy the .deb out
CMD ["/bin/bash"]
