# Guia de Instalação e Uso do Caninos Loucos SDK

## Introdução

Este documento detalha o processo de instalação e configuração do Caninos Loucos SDK em um sistema operacional baseado em Linux. O guia abrange a preparação do ambiente, a instalação de todas as dependências necessárias, a configuração de permissões de hardware, a instalação do SDK e um exemplo prático de como utilizá-lo para interagir com os pinos GPIO.

---

## Passos de Instalação

### Passo 1 – Atualizar o Sistema

É fundamental iniciar com a atualização dos pacotes do sistema para garantir que todas as dependências sejam instaladas em suas versões mais recentes e estáveis.

```bash
sudo apt update
```

### Passo 2 – Instalar Dependências

Instale as bibliotecas e ferramentas de desenvolvimento essenciais para o Python, que são pré-requisitos para o SDK.

```bash
sudo apt install python3-dev python3-pip python3-setuptools libffi-dev libssl-dev curl
```

### Passo 3 – Criar Ambiente Virtual

Para evitar conflitos de dependência com outros projetos ou com os pacotes do sistema, crie um ambiente virtual isolado.

```bash
python3 -m venv venv
```

### Passo 4 – Ativar o Ambiente Virtual

Para utilizar o ambiente virtual, você deve ativá-lo. O nome do ambiente (venv) aparecerá no seu terminal, indicando que ele está ativo.

```bash
source venv/bin/activate
```

### Passo 5 – Atualizar o pip

Dentro do ambiente virtual, atualize o gerenciador de pacotes do Python.

```bash
pip3 install --upgrade pip
```

### Passo 6 – Instalar gpiod

Instale a versão específica da biblioteca gpiod requerida pelo Caninos Loucos SDK.

```bash
pip3 install "gpiod==1.5.4"
```

### Passo 7 – Instalar o Caninos Loucos SDK

Instale o SDK principal através do pip.

```bash
pip3 install caninos-sdk
```

### Passo 8 – Atualizar o Arquivo pin.py

Para garantir a compatibilidade e o funcionamento correto, é necessário substituir o arquivo pin.py da instalação padrão.

1. Primeiro, faça o download ou clone o repositório a seguir, que contém os arquivos atualizados:

   - https://github.com/ThalysRD/caninos-sdk

2. Navegue até a pasta de pacotes do seu ambiente virtual. A versão do Python (ex: python3.11) pode variar.

```bash
cd venv/lib/python3.11/site-packages/caninos_sdk
```

3. Copie o arquivo pin.py do repositório que você baixou no passo 1 para este diretório, substituindo o arquivo existente.

### Passo 9 – Configurar Permissões dos Periféricos

Para que o SDK possa acessar o hardware da placa, você precisa executar um script de configuração de permissões.

1. Localize o arquivo `setup-permissions.sh`. Ele deve estar na pasta principal do repositório que você baixou no passo anterior. Caso não o encontre, baixe-o diretamente do repositório.

2. Execute os seguintes comandos para dar permissão de execução ao script e depois rodá-lo:

```bash
sudo chmod +x ./setup-permissions.sh
sudo ./setup-permissions.sh
```

### Passo 10 – Instalar IDE (Opcional)

Se desejar, você pode instalar uma IDE como o IDLE.

```bash
sudo apt-get install idle3
```

**Aviso Importante:** Para executar os códigos que utilizam o Caninos Loucos SDK, não use a IDE, pois ela não reconhece o ambiente virtual. Utilize sempre o terminal com o ambiente ativado.

---

## Como Rodar os Códigos

### Iniciando o Ambiente Virtual

Sempre que for trabalhar com o SDK em um novo terminal, lembre-se de ativar o ambiente virtual:

```bash
source venv/bin/activate
```

### Executando um Script

Para executar seus scripts Python, utilize o terminal. Por exemplo, se você salvar o código de exemplo como `exemplo.py`:

```bash
python3 exemplo.py
```

## Exemplo de Código

Este código demonstra como controlar um pino GPIO (neste caso, o pino 15) para acender e apagar um LED.

```python
# importa a SDK
import time
import caninos_sdk as k9

# instancia o objeto labrador
labrador = k9.Labrador()

# habilita o pino 15 como saída, e dá a ele o apelido "led_status"
labrador.pin15.enable_gpio(k9.Pin.Direction.OUTPUT, alias="led_status")

# liga o "led_status"
labrador.led_status.high()
time.sleep(2)

# desliga o "led_status"
labrador.led_status.low()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
