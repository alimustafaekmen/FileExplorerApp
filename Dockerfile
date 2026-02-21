# =============================================================================
# Dockerfile - Docker Configuration / Docker Yapılandırması
# =============================================================================
# This Dockerfile creates a container that can run the Tkinter-based
# file explorer using X11 display forwarding.
#
# Bu Dockerfile, Tkinter tabanlı dosya gezginini X11 ekran yönlendirmesi
# kullanarak çalıştırabilen bir konteyner oluşturur.
#
# Build / Derleme:
#   docker build -t file-explorer-app .
#
# Run / Çalıştırma (Linux):
#   docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix file-explorer-app
#
# Run / Çalıştırma (macOS - XQuartz gerekli):
#   xhost +localhost
#   docker run -e DISPLAY=host.docker.internal:0 file-explorer-app
# =============================================================================

# Use Python 3.11 slim base image / Python 3.11 slim temel imajını kullan
FROM python:3.11-slim

# Set working directory inside the container
# Konteyner içinde çalışma dizinini ayarla
WORKDIR /app

# Install system packages needed for Tkinter and X11
# Tkinter ve X11 için gerekli sistem paketlerini kur
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-tk \
    tk \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
# Proje dosyalarını konteynere kopyala
COPY src/ ./src/
COPY run.py .

# Set the default command to run the application
# Varsayılan komutu uygulamayı çalıştırmak olarak ayarla
CMD ["python", "run.py"]
