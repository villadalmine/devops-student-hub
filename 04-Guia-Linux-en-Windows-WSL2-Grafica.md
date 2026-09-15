# Linux con gráfica en Windows, sin VirtualBox (WSL2 + WSLg)

> Guía para los alumnos (y para validar labs). Reemplaza a VirtualBox para casi todo:
> WSL2 corre un kernel Linux real y **WSLg** te muestra las ventanas gráficas de Linux
> directo en el escritorio de Windows, con sonido incluido. Sin configurar nada.
>
> **Destino:** repo del hub de alumnos (`devops-student-hub`). Verificado el 2026-09-15 en
> Windows 11 + Rocky Linux 10.2. Un lab que anda acá anda igual en la VM del curso.

## Qué es y por qué

- **WSL2**: una máquina virtual liviana de Microsoft con un kernel Linux de verdad. Arranca
  en segundos, comparte disco y red con Windows, y no te come la RAM como una VM entera.
- **WSLg**: la capa gráfica que ya viene con WSL2 en Windows 11. Cada app Linux con ventana
  (un editor, `xeyes`, `wireshark`, un navegador) aparece como una ventana más de Windows.
  Trae **X11** (`DISPLAY=:0`), **Wayland** (`WAYLAND_DISPLAY=wayland-0`) y **audio** (PulseAudio).
- **Cubrimos las dos familias**: una distro **rpm** (Rocky/Fedora, como el CentOS del curso) y
  una **deb** (Ubuntu/Debian). Los comandos de administración cambian entre familias
  (`dnf` vs `apt`), así que conviene tener las dos.

## Requisitos

- Windows 11 (WSLg viene incluido). En Windows 10 también anda con WSL actualizado.
- Virtualización activada en la BIOS (casi siempre ya lo está).

## 1. Instalar WSL (una sola vez)

Abrí **PowerShell como administrador** y:

```powershell
wsl --install --no-distribution   # instala el motor WSL2 sin ninguna distro todavía
wsl --update                      # asegura el kernel y WSLg al día
wsl --version                     # verificá: debe listar "WSLg"
```

Reiniciá Windows si te lo pide.

## 2. Instalar las distros

Listá lo disponible y elegí. Cubrí las dos familias:

```powershell
wsl --list --online               # ver el catálogo

# Familia deb (Ubuntu):
wsl --install -d Ubuntu-24.04

# Familia rpm — Fedora desde el catálogo, o importá Rocky/CentOS (ver nota):
wsl --install -d FedoraLinux-42
```

La **primera vez** que entrás a Ubuntu te pide crear un usuario y contraseña (los tuyos, para
esa distro). En el curso usamos `educacionit` / `educacionit` para que coincida con la VM.

> **Nota rpm:** si el catálogo `--list --online` no trae Rocky/CentOS, se importan desde su
> imagen oficial de contenedor con `wsl --import` (una carpeta destino + el rootfs `.tar`).
> Fedora sí suele estar en el catálogo y sirve igual para practicar `dnf`.

## 3. Probar que la gráfica anda (WSLg)

Entrá a la distro y comprobá que el servidor gráfico está puesto **solo**:

```bash
echo $DISPLAY           # -> :0
echo $WAYLAND_DISPLAY   # -> wayland-0
ls /mnt/wslg            # está montado: distro, PulseServer, etc.
```

Instalá una app gráfica chica y lanzala — tiene que **abrirse una ventana en tu escritorio**:

```bash
# Rocky/Fedora (rpm):
sudo dnf install -y xterm && xterm

# Ubuntu/Debian (deb):
sudo apt update && sudo apt install -y x11-apps && xeyes
```

Si ves la ventana, la gráfica funciona. No hace falta ningún servidor X extra (VcXsrv, Xming):
WSLg ya lo trae.

## 4. Usarlo como la VM del curso

```bash
wsl -d Ubuntu-24.04        # entrar a una distro puntual
wsl -d rocky -u root       # entrar como root, sin crear usuario
wsl --shutdown             # apagar todas las distros (libera RAM)
```

- El disco de Windows está en `/mnt/c`. La home de Linux vive adentro de la distro (rápida).
- `code .` abre VS Code de Windows sobre la carpeta de Linux (integración automática).
- Para labs con Docker, Docker Desktop ya expone su motor a las distros WSL2.

## Cuándo sí seguir usando VirtualBox

WSL2 cubre casi todo el curso. Quedan para VirtualBox (o una VM real) los temas que tocan el
arranque de la máquina, porque WSL usa su propio kernel y no bootea como una PC normal:

- **GRUB y el gestor de arranque**, `grub2-mkconfig`, editar entradas de boot.
- **LVM sobre discos reales** y particionado físico de bajo nivel (`fdisk` en un disco entero).
- **systemd como PID 1 completo** en escenarios de arranque/targets (en WSL corre, pero acotado).

Para todo lo demás —permisos, usuarios, procesos, redes, paquetes, scripting, storage a nivel
archivo, servicios— WSL2 alcanza y sobra, y es mucho más liviano que VirtualBox.
