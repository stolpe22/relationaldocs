FROM node:20
 
ARG TZ
ENV TZ="$TZ"
 
ARG CLAUDE_CODE_VERSION=latest
 
# Instala ferramentas de dev + iptables/ipset para firewall
RUN apt-get update && apt-get install -y --no-install-recommends \
  less git procps sudo fzf zsh man-db unzip gnupg2 gh \
  iptables ipset iproute2 dnsutils aggregate jq nano vim \
  python3 python3-pip python3-venv python3-dev build-essential \
  libaio1 wget \
  && apt-get clean && rm -rf /var/lib/apt/lists/*


# Oracle Instant Client 21.x (suporta Oracle 12c+)
RUN wget -q https://download.oracle.com/otn_software/linux/instantclient/2115000/instantclient-basic-linux.x64-21.15.0.0.0dbru.zip \
  && unzip -q instantclient-basic-linux.x64-21.15.0.0.0dbru.zip -d /opt/oracle \
  && rm instantclient-basic-linux.x64-21.15.0.0.0dbru.zip \
  && chmod -R a+rX /opt/oracle/instantclient_21_15 \
  && echo /opt/oracle/instantclient_21_15 > /etc/ld.so.conf.d/oracle.conf \
  && ldconfig

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_15:$LD_LIBRARY_PATH

# sqlnet.ora: desabilita OOB breaks — necessário para conexões via SSH tunnel
RUN mkdir -p /opt/oracle/instantclient_21_15/network/admin && \
  printf 'DISABLE_OOB=ON\nSQLNET.EXPIRE_TIME=10\n' \
  > /opt/oracle/instantclient_21_15/network/admin/sqlnet.ora

ENV TNS_ADMIN=/opt/oracle/instantclient_21_15/network/admin

# Python/uv toolchain + dependências do projeto instaladas globalmente
RUN ln -sf /usr/bin/python3 /usr/local/bin/python && \
  ln -sf /usr/bin/pip3 /usr/local/bin/pip && \
  python3 -m pip install --no-cache-dir --break-system-packages --upgrade pip setuptools wheel && \
  python3 -m pip install --no-cache-dir --break-system-packages uv && \
  python3 -m pip install --no-cache-dir --break-system-packages \
    fastapi "uvicorn[standard]" oracledb paramiko sshtunnel pydantic python-dotenv \
    pytest pytest-cov pytest-asyncio pytest-mock httpx ruff mypy && \
  ln -sf $(python3 -c "import sysconfig; print(sysconfig.get_path('scripts'))") /usr/local/bin/python-scripts || true
 
RUN mkdir -p /usr/local/share/npm-global && \
  chown -R node:node /usr/local/share
 
ARG USERNAME=node
 
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
  && mkdir /commandhistory \
  && touch /commandhistory/.bash_history \
  && chown -R $USERNAME /commandhistory
 
ENV DEVCONTAINER=true
 
RUN mkdir -p /workspace /home/node/.claude && \
  chown -R node:node /workspace /home/node/.claude
 
WORKDIR /workspace
 
ARG GIT_DELTA_VERSION=0.18.2
RUN ARCH=$(dpkg --print-architecture) && \
  wget "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  sudo dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"
 
USER node
 
ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global
ENV PATH=$PATH:/usr/local/share/npm-global/bin
ENV SHELL=/bin/zsh
ENV EDITOR=nano
ENV VISUAL=nano
ENV UV_LINK_MODE=copy
ENV UV_PYTHON=python3
 
ARG ZSH_IN_DOCKER_VERSION=1.2.0
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
  -p git -p fzf \
  -a "source /usr/share/doc/fzf/examples/key-bindings.zsh" \
  -a "source /usr/share/doc/fzf/examples/completion.zsh" \
  -a "export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
  -x
 
# ⭐ Instala o Claude Code
RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}
 
COPY init-firewall.sh /usr/local/bin/
USER root
RUN chmod +x /usr/local/bin/init-firewall.sh && \
  echo "node ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/node-firewall && \
  chmod 0440 /etc/sudoers.d/node-firewall
USER node