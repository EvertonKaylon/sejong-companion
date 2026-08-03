# BUG-06: Falha de Bind de Redes no Windows (`FLET_SERVER_IP="0.0.0.0"`)

- **Severidade**: 🟠 Alta
- **Módulo**: `main.py`
- **Componente**: Flet Web Server / Network Binding

---

## 1. Descrição do Problema

Ao tentar executar o aplicativo no ambiente Windows através do comando `python main.py`, o processo falhava imediatamente ao tentar abrir a página no navegador com uma das seguintes mensagens:
- `ERR_ADDRESS_INVALID` (no Chrome/Edge ao abrir `http://0.0.0.0:8554`)
- `OSError: [WinError 10049] getaddrinfo failed` (ao tentar usar wildcard `*`)

---

## 2. Causa Raiz Técnica

O Flet gerencia o servidor HTTP embutido e automaticamente invoca a abertura do navegador padrão do usuário:

1. **IP `0.0.0.0` no Windows**: Quando `FLET_SERVER_IP` é configurado como `"0.0.0.0"`, o Flet instrui o sistema operacional a abrir o navegador no endereço `http://0.0.0.0:8554`. No Windows, `0.0.0.0` não é resolvido como loopback local de destino, resultando em `ERR_ADDRESS_INVALID`.
2. **Wildcard `*`**: O Windows Sockets (Winsock) rejeita a string `"*"` na função nativa `getaddrinfo()`, quebrando a inicialização do socket servidor.

---

## 3. Solução Aplicada

Definimos formalmente o IP de bind como `"127.0.0.1"` por padrão no [main.py](file:///c:/Users/Pichau/Documents/sejong_companion/main.py), com documentação clara no código para testes em rede local/mobile.

### Código Antes (Falhava no Windows):
```python
# Tentar 0.0.0.0 quebra o redirecionamento automático do navegador no Windows
os.environ["FLET_SERVER_IP"] = "0.0.0.0"
```

### Código Depois (Confiável no Windows):
```python
# Rodando em 127.0.0.1 (localhost) por padrão para garantir bind no Windows
os.environ["FLET_SERVER_IP"] = "127.0.0.1"

if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="127.0.0.1", port=8554, assets_dir="assets")
```

---

## 4. Regra Preventiva

> [!NOTE]
> Para desenvolvimento local no Windows, utilize sempre `127.0.0.1`. Se precisar testar no celular via Wi-Fi, altere para `0.0.0.0` e acesse pelo IP local da máquina (`http://192.168.x.x:8554`) no navegador do celular.
