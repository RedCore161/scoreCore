FROM niekandresen/deeplabcut:2.2.1.1
RUN apt-get -y update && apt-get install -y \
    wget \
    nano \
    git


RUN apt install libgl1-mesa-glx -y
RUN apt-get install "ffmpeg"\
    "libsm6"\
    "libxext6"  -y

WORKDIR /wd

RUN pip install opencv-python\
    tables\
    pandas\
    moviepy\
    openpyxl\
    scikit-image\
    torch

COPY ./docker/deeplab/detector .

CMD ["tail", "-f", "/dev/null"]

