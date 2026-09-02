# Implantação privada pela Tailscale

Este procedimento mantém a aplicação na porta `8010`, acessível somente pela
rede Tailscale, e não grava a chave da B.AI no histórico do terminal.

## 1. Backup e atualização dos arquivos

Considere que o pacote foi enviado para `/home/eduardo`.

```bash
cd /home/eduardo

PACOTE=$(ls -t AgenteJuridicoDeCorrecao_BAI_Tailscale_*.tar.gz | head -1)
RELEASE="/home/eduardo/agente-juridico-release-$(date +%Y%m%d_%H%M%S)"
BACKUP="/home/eduardo/AgenteJuridicoDeCorrecao_backup_$(date +%Y%m%d_%H%M%S).tar.gz"

test -n "$PACOTE" || { echo "Pacote não encontrado"; exit 1; }
mkdir -p "$RELEASE"
tar --no-same-owner -xzf "$PACOTE" -C "$RELEASE"

tar -czf "$BACKUP" \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  /home/eduardo/AgenteJuridicoDeCorrecao

cp -a "$RELEASE"/. /home/eduardo/AgenteJuridicoDeCorrecao/
echo "Backup: $BACKUP"
```

## 2. Dependências e testes

```bash
cd /home/eduardo/AgenteJuridicoDeCorrecao

.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m compileall -q app tests
.venv/bin/python -m unittest discover -s tests -v
```

Somente prossiga se todos os testes terminarem com `OK`.

## 3. Chave da B.AI

```bash
read -rsp "Cole a chave da B.AI: " BAI_SECRET
echo

sudo install -m 600 -o root -g root /dev/null \
  /etc/agente-juridico-correcao.env

printf 'BAI_API_KEY=%s\nBAI_MODEL=qwen3.8-flash\n' "$BAI_SECRET" \
  | sudo tee /etc/agente-juridico-correcao.env >/dev/null

unset BAI_SECRET
```

## 4. Restringir o serviço à Tailscale

```bash
TS_IP=$(tailscale ip -4 | head -1)

case "$TS_IP" in
  100.*) echo "IP Tailscale confirmado: $TS_IP" ;;
  *) echo "IP Tailscale inválido: $TS_IP"; exit 1 ;;
esac

sudo mkdir -p \
  /etc/systemd/system/agente-juridico-correcao.service.d

sudo tee \
  /etc/systemd/system/agente-juridico-correcao.service.d/override.conf \
  >/dev/null <<EOF
[Service]
EnvironmentFile=/etc/agente-juridico-correcao.env
ExecStart=
ExecStart=/home/eduardo/AgenteJuridicoDeCorrecao/.venv/bin/uvicorn app.main:app --host $TS_IP --port 8010 --workers 1
EOF

sudo ufw allow in on tailscale0 to any port 8010 proto tcp \
  comment 'Assistente Contratual via Tailscale'

sudo systemctl daemon-reload
sudo systemctl restart agente-juridico-correcao.service
```

## 5. Validação

```bash
echo "===== SERVIÇO ====="
systemctl --no-pager --full status agente-juridico-correcao.service

echo
echo "===== PORTA ====="
sudo ss -ltnp 'sport = :8010'

echo
echo "===== HEALTHCHECK ====="
curl -fsS "http://$TS_IP:8010/health"

echo
echo "===== LOGS RECENTES ====="
journalctl -u agente-juridico-correcao.service -n 40 --no-pager

echo
echo "Abra no dispositivo conectado à Tailscale:"
echo "http://$TS_IP:8010"
```

O resultado esperado da porta deve mostrar o IP Tailscale, nunca `0.0.0.0`.
