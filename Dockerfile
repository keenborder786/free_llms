FROM knthony/run_chrome_driver_in_container

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

RUN mkdir free_llms
WORKDIR /opt/free_llms

COPY pyproject.toml poetry.lock /opt/free_llms/
COPY src/free_llms /opt/free_llms/src/free_llms
COPY tests /opt/free_llms/tests
RUN poetry install --with dev
ENV CHROME_VERSION=108
ENV VIRTUAL_ENV=/opt/free_llms/.venv \
    PATH="/opt/free_llms/.venv/bin:$PATH"

RUN cp /entrypoint.sh /opt/free_llms
ENTRYPOINT ["/entrypoint.sh"]
CMD ["pytest"]