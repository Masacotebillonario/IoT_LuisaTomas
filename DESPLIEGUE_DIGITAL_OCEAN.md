# Guía de despliegue en Digital Ocean

## 1. Crear una Droplet en Digital Ocean

1. Ve a [Digital Ocean](https://www.digitalocean.com)
2. Crea una cuenta o inicia sesión
3. Haz clic en "Create" → "Droplets"
4. Elige:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic (5$/mes es suficiente para empezar)
   - **Region**: Elige la más cercana
5. Haz clic en "Create Droplet"

## 2. Conectar por SSH

```bash
ssh root@tu_ip_publica
```

## 3. Preparar el servidor

```bash
# Actualizar paquetes
apt update && apt upgrade -y

# Instalar Python y herramientas
apt install -y python3 python3-pip python3-venv git wget curl nginx supervisor

# Crear usuario para la app
useradd -m -s /bin/bash iotapp
su - iotapp
```

## 4. Clonar el repositorio (o copiar archivos)

```bash
cd /home/iotapp
git clone <tu-repositorio>
# O copiar manualmente los archivos
```

## 5. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 6. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus datos
nano .env
```

## 7. Configurar Supervisor (para ejecutar Gunicorn)

```bash
sudo nano /etc/supervisor/conf.d/iotapp.conf
```

Pega esto:
```ini
[program:iotapp]
directory=/home/iotapp/Monitoreo_IoT
command=/home/iotapp/Monitoreo_IoT/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 wsgi:app
user=iotapp
autostart=true
autorestart=true
stderr_logfile=/var/log/iotapp.err.log
stdout_logfile=/var/log/iotapp.out.log
```

## 8. Recargar supervisor

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start iotapp
```

## 9. Configurar Nginx (proxy inverso)

```bash
sudo nano /etc/nginx/sites-available/iotapp
```

Pega esto:
```nginx
server {
    listen 80;
    server_name tu_dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 10. Habilitar el sitio en Nginx

```bash
sudo ln -s /etc/nginx/sites-available/iotapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 11. Configurar SSL (HTTPS) con Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu_dominio.com
```

## 12. Verificar status

```bash
sudo supervisorctl status
sudo systemctl status nginx
```

## Troubleshooting

Ver logs:
```bash
tail -f /var/log/iotapp.out.log
tail -f /var/log/iotapp.err.log
sudo tail -f /var/log/nginx/error.log
```

Reiniciar la app:
```bash
sudo supervisorctl restart iotapp
```
