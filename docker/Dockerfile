FROM python:3.13-slim-bookworm AS build

ENV DEBIAN_FRONTEND=noninteractive \
    PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:/usr/local/lib/x86_64-linux-gnu/pkgconfig \
    LD_LIBRARY_PATH=/usr/local/lib

ARG ASTRON_REF=master

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    cmake \
    g++ \
    git \
    make \
    pkg-config \
    libboost-all-dev \
    libicu-dev \
    libssl-dev \
    libsasl2-dev \
    libsnappy-dev \
    libuv1-dev \
    libyaml-cpp-dev \
    zlib1g-dev \
    libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch 1.24.4 https://github.com/mongodb/mongo-c-driver.git /tmp/mongo-c-driver \
    && cmake -S /tmp/mongo-c-driver -B /tmp/mongo-c-driver/cmake-build \
       -DCMAKE_BUILD_TYPE=Release \
       -DCMAKE_INSTALL_PREFIX=/usr/local \
       -DBUILD_VERSION=1.24.4 \
       -DENABLE_TESTS=OFF \
    && cmake --build /tmp/mongo-c-driver/cmake-build --target install --parallel 2 \
    && ldconfig

RUN git clone --depth 1 --branch r3.8.0 https://github.com/mongodb/mongo-cxx-driver.git /tmp/mongo-cxx-driver \
    && cmake -S /tmp/mongo-cxx-driver -B /tmp/mongo-cxx-driver/cmake-build \
       -DCMAKE_BUILD_TYPE=Release \
       -DBUILD_VERSION=3.8.0 \
       -DCMAKE_INSTALL_PREFIX=/usr/local \
       -DCMAKE_PREFIX_PATH=/usr/local \
       -DBSONCXX_POLY_USE_BOOST=ON \
       -DENABLE_TESTS=OFF \
       -DCMAKE_INSTALL_RPATH=/usr/local/lib \
       -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON \
    && cmake --build /tmp/mongo-cxx-driver/cmake-build --target install --parallel 2 \
    && ldconfig

RUN git clone --depth 1 --branch "${ASTRON_REF}" https://github.com/Astron/Astron.git /tmp/Astron \
    && cmake -S /tmp/Astron -B /tmp/Astron/build \
       -DCMAKE_BUILD_TYPE=Release \
       -DCMAKE_PREFIX_PATH=/usr/local \
       -DCMAKE_INSTALL_RPATH=/usr/local/lib \
       -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON \
    && cmake --build /tmp/Astron/build --parallel 2 \
    && install -D /tmp/Astron/build/astrond /out/astrond

FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    LD_LIBRARY_PATH=/usr/local/lib \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPYCACHEPREFIX=/tmp/altis-pycache

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libasound2 \
    libgl1 \
    libglib2.0-0 \
    libicu72 \
    libsm6 \
    libssl3 \
    libsasl2-2 \
    libsnappy1v5 \
    libuv1 \
    libyaml-cpp0.7 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libzstd1 \
    netcat-openbsd \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/lib/ /usr/local/lib/
COPY --from=build /out/astrond /usr/local/bin/astrond

ARG PANDA3D_VERSION=1.10.16

RUN ldconfig \
    && python -m pip install --no-cache-dir --pre \
       "panda3d==${PANDA3D_VERSION}" \
       pymongo==4.9.2 \
       StrEnum==0.4.15 \
       six==1.17.0

COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh && mkdir -p /var/log/altis

WORKDIR /app
ENTRYPOINT ["/usr/local/bin/start.sh"]
