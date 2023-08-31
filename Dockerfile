FROM amazon/aws-glue-libs:glue_libs_4.0.0_image_01

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CMD [ "python", "./main.py" ]