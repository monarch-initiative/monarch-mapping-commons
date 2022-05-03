# Final ODK image
# (built upon the odklite image)
FROM obolibrary/odkfull:latest
LABEL maintainer="nicolas.matentzoglu@gmail.com"

# Install boomer
ENV BOOMER_VERSION=0.2
ENV PATH "/tools/boomer/bin:$PATH"
RUN wget -nv https://github.com/INCATools/boomer/releases/download/v$BOOMER_VERSION/boomer-$BOOMER_VERSION.tgz \
&& tar -zxvf boomer-$BOOMER_VERSION.tgz \
&& mv boomer-$BOOMER_VERSION /tools/boomer \
&& chmod +x /tools/boomer/bin/boomer

RUN pip install --upgrade pip &&\
  pip install --upgrade --no-deps --force-reinstall sssom==0.3.10

