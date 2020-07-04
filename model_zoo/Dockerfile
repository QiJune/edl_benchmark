FROM tensorflow/tensorflow:2.1.0-py3 as base

RUN pip install elasticdl_preprocessing --extra-index-url=https://pypi.org/simple

RUN pip install elasticdl --extra-index-url=https://pypi.org/simple
ENV PATH /usr/local/lib/python3.6/dist-packages/elasticdl/go/bin:$PATH

COPY . /model_zoo
RUN pip install -r /model_zoo/requirements.txt --extra-index-url=https://pypi.org/simple

RUN mkdir /data && python /model_zoo/image_label.py --dataset mnist \
        --records_per_shard 4096 /data

