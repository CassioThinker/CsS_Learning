# API Flask Simples com Docker e Kubernetes na AWS

Este projeto demonstra o desenvolvimento de uma API REST simples em Python usando Flask, seu empacotamento em um contêiner Docker, e a configuração para implantação em um cluster Kubernetes (EKS) na AWS, com gerenciamento de código-fonte via Git.

## Estrutura do Projeto

-   `app.py`: O código-fonte da API Flask.
-   `requirements.txt`: Dependências Python da API.
-   `Dockerfile`: Instruções para construir a imagem Docker da aplicação.
-   `.dockerignore`: Arquivos e diretórios a serem ignorados durante o build da imagem Docker.
-   `deployment.yaml`: Manifesto de Deployment do Kubernetes para a API.
-   `service.yaml`: Manifesto de Service do Kubernetes para expor a API.
-   `aws_deployment_instructions.md`: Documento detalhado com os passos para implantação na AWS.
-   `.gitignore`: Arquivos e diretórios a serem ignorados pelo Git.

## 1. API Flask

A API é uma aplicação Flask simples que retorna "Hello, World!" na rota raiz.

### `app.py`
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
```

### `requirements.txt`
```
Flask==2.2.2
Werkzeug==2.2.2
```

## 2. Dockerização

O `Dockerfile` define como a aplicação Flask é empacotada em uma imagem Docker.

### `Dockerfile`
```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### `.dockerignore`
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.env
.venv
.git
.vscode/
*.log
.cache/
.config/
.local/
.nvm/
```

### Construir e Executar a Imagem Docker

Para construir a imagem Docker:

```bash
sudo docker build -t python-flask-api .
```

Para executar o contêiner Docker localmente e testar a API:

```bash
sudo docker run -p 5000:5000 python-flask-api
```

Você pode testar a API acessando `http://localhost:5000` em seu navegador ou usando `curl`:

```bash
curl http://localhost:5000
```

## 3. Kubernetes Manifests

Os arquivos `deployment.yaml` e `service.yaml` definem como a aplicação será implantada e exposta em um cluster Kubernetes.

### `deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-flask-api-deployment
  labels:
    app: python-flask-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: python-flask-api
  template:
    metadata:
      labels:
        app: python-flask-api
    spec:
      containers:
      - name: python-flask-api
        image: YOUR_ECR_IMAGE_URI # Substitua pela URI da sua imagem no ECR
        ports:
        - containerPort: 5000
```

### `service.yaml`
```yaml
apiVersion: v1
kind: Service
metadata:
  name: python-flask-api-service
spec:
  selector:
    app: python-flask-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: LoadBalancer
```

## 4. Implantação na AWS (EKS)

Para instruções detalhadas sobre como implantar esta API em um cluster Kubernetes na AWS (EKS), incluindo a construção e push da imagem para o Amazon ECR, configuração do cluster EKS e aplicação dos manifests do Kubernetes, consulte o arquivo `Instruções de Implantação na AWS.md`.

## 5. Gerenciamento de Código-Fonte com Git

O projeto é versionado usando Git. Os comandos básicos para inicializar o repositório, adicionar arquivos e fazer commits são:

```bash
git init
git add .
git commit -m "Initial commit: Flask API, Dockerfile, Kubernetes manifests, and AWS deployment instructions"
```

O arquivo `.gitignore` garante que arquivos e diretórios desnecessários (como caches e dependências de ambiente) não sejam incluídos no repositório.

### `.gitignore`
```
.nvm/
.local/
```

---

**Autor:** Cássio Thinker
**Data:** 03 de agosto de 2024

