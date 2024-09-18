FROM iregistry.baidu-int.com/baidu-base/python:3.12-alpine3.19

RUN apk add curl wget bash zip bns python3.12-pip

RUN pip install --no-cache-dir requests omegaconf bce-python-sdk

WORKDIR /home/work

RUN chown -R work:work /home/work/ && chmod -R 775 /home/work/

COPY --chown=work:work output/reflow_check/ /home/work/reflow_check/

USER work

ENTRYPOINT []

CMD ["bash", "/home/work/reflow_check/entrypoint.sh"]