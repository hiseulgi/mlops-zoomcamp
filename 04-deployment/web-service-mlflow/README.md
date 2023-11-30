## Deploying a model as a web-service

* Take the code from the previous video
* Train another model, register with MLflow
* Put the model into a scikit-learn pipeline
* Model deployment with tracking server
* Model deployment without the tracking server


```bash
docker build -t ride-duration-prediction-service:mlflow-v1 .
```

```bash
docker run -it --rm -p 9696:9696  ride-duration-prediction-service:mlflow-v1
```