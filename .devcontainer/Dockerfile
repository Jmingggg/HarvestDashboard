FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    ca-certificates \
    curl \
    git \
    htop \
    llvm \
    nano \
    sudo \
    tree \
    wget \
    # Python build dependencies
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libxmlsec1-dev \
    tk-dev \
    xz-utils \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=vscode
ARG USER_UID=1024
RUN useradd --uid $USER_UID --create-home $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

ENV PYENV_ROOT="/home/$USERNAME/.pyenv"
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
ENV PYTHON_VERSION=3.12.12

RUN curl https://pyenv.run | bash \
    && pyenv install $PYTHON_VERSION \
    && pyenv global $PYTHON_VERSION

ENV PATH="/home/$USERNAME/.local/bin:$PATH"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /workspace

CMD ["bash"]
