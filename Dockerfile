# Final ODK image
# (built upon the odklite image)
FROM obolibrary/odkfull:latest
LABEL maintainer="nicolas.matentzoglu@gmail.com"

# Install boomer
ENV BOOMER_VERSION=0.2
ENV PATH "/tools/boomer/bin:$PATH"
RUN wget -nv https://github.com/INCATools/boomer/releases/download/v$BOOMER_VERSION/boomer-$BOOMER_VERSION.tgz && \
  tar -zxvf boomer-$BOOMER_VERSION.tgz && \
  mv boomer-$BOOMER_VERSION /tools/boomer && \
  chmod +x /tools/boomer/bin/boomer

# Install python dependencies
RUN pip install --upgrade pip && \
  pip install --upgrade --force-reinstall sssom==0.3.10 curies pandas j2cli

# Install nodejs for og2dot
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash - && \
  apt-get install -y nodejs && \
  npm install -g obographviz
