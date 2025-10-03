# Instruções de Implantação na AWS

Este documento detalha os passos necessários para implantar a API Flask em um cluster Kubernetes (EKS) na AWS.

## Pré-requisitos

Antes de iniciar, certifique-se de ter as seguintes ferramentas instaladas e configuradas:

-   **AWS CLI**: Configurado com credenciais que tenham permissões para ECR e EKS.
-   **Docker**: Para construir e empurrar imagens.
-   **kubectl**: Para interagir com o cluster Kubernetes.
-   **eksctl**: Ferramenta CLI para criar e gerenciar clusters EKS (opcional, mas recomendado).

## 1. Construir e Publicar a Imagem Docker no Amazon ECR

1.  **Autenticar o Docker no ECR:**

    ```bash
    aws ecr get-login-password --region <SUA_REGIAO> | docker login --username AWS --password-stdin <SEU_ID_CONTA>.dkr.ecr.<SUA_REGIAO>.amazonaws.com
    ```
    Substitua `<SUA_REGIAO>` pela região da AWS (ex: `us-east-1`) e `<SEU_ID_CONTA>` pelo seu ID de conta AWS.

2.  **Criar um repositório ECR (se ainda não existir):**

    ```bash
    aws ecr create-repository \
        --repository-name python-flask-api \
        --region <SUA_REGIAO>
    ```

3.  **Construir a imagem Docker:**

    ```bash
    docker build -t python-flask-api .
    ```

4.  **Taggear a imagem para o ECR:**

    ```bash
    docker tag python-flask-api:latest <SEU_ID_CONTA>.dkr.ecr.<SUA_REGIAO>.amazonaws.com/python-flask-api:latest
    ```

5.  **Empurrar a imagem para o ECR:**

    ```bash
    docker push <SEU_ID_CONTA>.dkr.ecr.<SUA_REGIAO>.amazonaws.com/python-flask-api:latest
    ```

## 2. Configurar o Cluster Amazon EKS

1.  **Criar um cluster EKS (se ainda não tiver um):**

    Você pode usar `eksctl` para criar um cluster facilmente:

    ```bash
    eksctl create cluster \
        --name my-flask-cluster \
        --region <SUA_REGIAO> \
        --node-type t3.medium \
        --nodes 2
    ```

2.  **Configurar `kubectl` para usar o cluster EKS:**

    ```bash
    aws eks update-kubeconfig --name my-flask-cluster --region <SUA_REGIAO>
    ```

3.  **Verificar a conexão com o cluster:**

    ```bash
    kubectl get svc
    ```

## 3. Implantar a Aplicação no Kubernetes

1.  **Atualizar o `deployment.yaml`:**

    Edite o arquivo `deployment.yaml` e substitua `YOUR_ECR_IMAGE_URI` pela URI completa da imagem que você empurrou para o ECR. Exemplo:

    ```yaml
    image: <SEU_ID_CONTA>.dkr.ecr.<SUA_REGIAO>.amazonaws.com/python-flask-api:latest
    ```

2.  **Aplicar os manifests do Kubernetes:**

    ```bash
    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml
    ```

3.  **Verificar o status da implantação:**

    ```bash
    kubectl get deployments
    kubectl get pods
    kubectl get services
    ```

    Aguarde até que o LoadBalancer do serviço esteja provisionado e um `EXTERNAL-IP` seja atribuído. Isso pode levar alguns minutos.

4.  **Acessar a API:**

    Uma vez que o `EXTERNAL-IP` esteja disponível, você pode acessar sua API usando esse IP no seu navegador ou com `curl`:

    ```bash
    curl http://<EXTERNAL-IP>
    ```

## 4. Limpeza (Opcional)

Para remover os recursos da AWS:

1.  **Deletar os recursos do Kubernetes:**

    ```bash
    kubectl delete -f service.yaml
    kubectl delete -f deployment.yaml
    ```

2.  **Deletar o cluster EKS:**

    ```bash
    eksctl delete cluster --name my-flask-cluster --region <SUA_REGIAO>
    ```

3.  **Deletar a imagem do ECR:**

    ```bash
    aws ecr batch-delete-image \
        --repository-name python-flask-api \
        --image-ids imageTag=latest \
        --region <SUA_REGIAO>
    aws ecr delete-repository \
        --repository-name python-flask-api \
        --region <SUA_REGIAO>
    ```

