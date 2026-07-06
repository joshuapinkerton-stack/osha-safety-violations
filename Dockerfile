FROM apify/actor-python:3.14
COPY --chown=myuser:myuser requirements.txt ./
RUN pip install -r requirements.txt && pip freeze
COPY --chown=myuser:myuser . ./
RUN python -m compileall -q osha_safety_violations/
CMD ["python", "-m", "osha_safety_violations"]
