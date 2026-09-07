-- =====================================================================
--  Configuracion Oficial de Neovim para el Curso Cloud DevOps
--  Optimizada para correr DENTRO de paneles de Herdr (multiplexer).
--
--  Archivo de destino en Windows: %LOCALAPPDATA%\nvim\init.lua
--  Se despliega automaticamente con:
--    powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1
--
--  No requiere plugins ni gestor de plugins: funciona apenas se instala
--  Neovim, incluso sin conexion a internet en el aula.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. LIDER Y OPCIONES BASE
-- ---------------------------------------------------------------------
vim.g.mapleader = " "
vim.g.maplocalleader = " "

local opt = vim.opt

opt.number = true
opt.relativenumber = true
opt.cursorline = true
opt.signcolumn = "yes"
opt.scrolloff = 8
opt.sidescrolloff = 8
opt.wrap = false
opt.splitright = true
opt.splitbelow = true
opt.showmode = false
opt.pumheight = 12

-- Indentacion por defecto (YAML, Terraform y Dockerfile usan 2 espacios)
opt.expandtab = true
opt.shiftwidth = 2
opt.tabstop = 2
opt.softtabstop = 2
opt.smartindent = true

-- Busqueda
opt.ignorecase = true
opt.smartcase = true
opt.incsearch = true
opt.hlsearch = true

-- Historial persistente de undo
opt.undofile = true
opt.swapfile = false
opt.backup = false

-- ---------------------------------------------------------------------
-- 2. AJUSTES ESPECIFICOS PARA VIVIR DENTRO DE UN MULTIPLEXER (HERDR)
-- ---------------------------------------------------------------------

-- Colores de 24 bits: Herdr y Ghostty los soportan. Sin esto, el tema
-- se ve con 16 colores planos dentro del panel.
if vim.fn.has("termguicolors") == 1 then
  opt.termguicolors = true
end

-- Latencia de Esc: en un multiplexer, un timeout alto hace que salir de
-- modo insercion se sienta "pegajoso". 10 ms lo vuelve instantaneo.
opt.timeoutlen = 400
opt.ttimeoutlen = 10
opt.updatetime = 250

-- El mouse funciona dentro del panel (seleccionar, redimensionar splits).
opt.mouse = "a"

-- El titulo del panel de Herdr muestra el archivo abierto.
opt.title = true
opt.titlestring = "nvim: %t"

-- Forma del cursor. Al salir de Neovim se restaura el cursor de bloque:
-- sin esto, el panel de Herdr queda con cursor de linea fina para siempre.
opt.guicursor = "n-v-c:block,i-ci-ve:ver25,r-cr:hor20,o:hor50"
vim.api.nvim_create_autocmd("VimLeave", {
  desc = "Restaurar el cursor de bloque al salir (evita cursor roto en Herdr)",
  callback = function()
    vim.opt.guicursor = "a:block"
  end,
})

-- Redibujar al recuperar el foco del panel (Herdr envia FocusGained).
vim.api.nvim_create_autocmd({ "FocusGained", "VimResume" }, {
  desc = "Refrescar la pantalla al volver al panel",
  command = "redraw!",
})

-- Releer el archivo si cambio en disco desde otro panel de Herdr.
opt.autoread = true
vim.api.nvim_create_autocmd({ "FocusGained", "BufEnter", "TermClose", "TermLeave" }, {
  desc = "Detectar cambios hechos desde otro panel",
  command = "checktime",
})

-- ---------------------------------------------------------------------
-- 3. PORTAPAPELES DE WINDOWS
--    Neovim usa win32yank si existe; si no, hacemos puente con PowerShell
--    para que 'y' y 'p' compartan el portapapeles con VS Code y el navegador.
-- ---------------------------------------------------------------------
if vim.fn.has("win32") == 1 and vim.fn.executable("win32yank.exe") == 0 then
  vim.g.clipboard = {
    name = "powershell-clipboard",
    copy = {
      ["+"] = { "powershell.exe", "-NoLogo", "-NoProfile", "-Command", "$input | Set-Clipboard" },
      ["*"] = { "powershell.exe", "-NoLogo", "-NoProfile", "-Command", "$input | Set-Clipboard" },
    },
    paste = {
      ["+"] = { "powershell.exe", "-NoLogo", "-NoProfile", "-Command", "Get-Clipboard -Raw" },
      ["*"] = { "powershell.exe", "-NoLogo", "-NoProfile", "-Command", "Get-Clipboard -Raw" },
    },
    cache_enabled = 0,
  }
end
opt.clipboard = "unnamedplus"

-- ---------------------------------------------------------------------
-- 4. TERMINAL INTEGRADA (:terminal) CON POWERSHELL
-- ---------------------------------------------------------------------
if vim.fn.has("win32") == 1 then
  local pwsh = vim.fn.executable("pwsh.exe") == 1 and "pwsh.exe" or "powershell.exe"
  opt.shell = pwsh
  opt.shellcmdflag = "-NoLogo -NoProfile -ExecutionPolicy RemoteSigned -Command"
  opt.shellquote = ""
  opt.shellxquote = ""
end

vim.api.nvim_create_autocmd("TermOpen", {
  desc = "Terminal integrada sin numeros de linea",
  callback = function()
    vim.opt_local.number = false
    vim.opt_local.relativenumber = false
    vim.opt_local.signcolumn = "no"
    vim.cmd("startinsert")
  end,
})

-- ---------------------------------------------------------------------
-- 5. ATAJOS DE TECLADO (SIN PISAR LOS DE HERDR)
--
--    Herdr reserva Ctrl+h/j/k/l para moverse entre PANELES, por lo que
--    aca se usa Alt+h/j/k/l para moverse entre las VENTANAS de Neovim.
--    Ctrl+w (prefijo nativo de ventanas de Neovim) queda libre porque en
--    config.toml de Herdr cerrar panel se reasigno a Ctrl+Shift+W.
-- ---------------------------------------------------------------------
local map = vim.keymap.set

-- Movimiento entre ventanas de Neovim
map("n", "<A-h>", "<C-w>h", { desc = "Ventana izquierda" })
map("n", "<A-j>", "<C-w>j", { desc = "Ventana abajo" })
map("n", "<A-k>", "<C-w>k", { desc = "Ventana arriba" })
map("n", "<A-l>", "<C-w>l", { desc = "Ventana derecha" })

-- Redimensionar ventanas
map("n", "<A-Up>", "<cmd>resize +2<cr>", { desc = "Mas alto" })
map("n", "<A-Down>", "<cmd>resize -2<cr>", { desc = "Mas bajo" })
map("n", "<A-Left>", "<cmd>vertical resize -4<cr>", { desc = "Mas angosto" })
map("n", "<A-Right>", "<cmd>vertical resize +4<cr>", { desc = "Mas ancho" })

-- Splits (mismo criterio que Herdr: derecha y abajo)
map("n", "<leader>sv", "<cmd>vsplit<cr>", { desc = "Split vertical" })
map("n", "<leader>sh", "<cmd>split<cr>", { desc = "Split horizontal" })

-- Archivos y buffers
map("n", "<leader>w", "<cmd>write<cr>", { desc = "Guardar" })
map("n", "<leader>q", "<cmd>quit<cr>", { desc = "Cerrar ventana" })
map("n", "<leader>e", "<cmd>Explore<cr>", { desc = "Explorador de archivos" })
map("n", "<leader>h", "<cmd>nohlsearch<cr>", { desc = "Limpiar resaltado" })
map("n", "<S-l>", "<cmd>bnext<cr>", { desc = "Buffer siguiente" })
map("n", "<S-h>", "<cmd>bprevious<cr>", { desc = "Buffer anterior" })

-- Terminal integrada: Esc vuelve a modo normal
map("t", "<Esc><Esc>", "<C-\\><C-n>", { desc = "Salir del modo terminal" })
map("n", "<leader>t", "<cmd>botright 15split | terminal<cr>", { desc = "Terminal abajo" })

-- Mover lineas seleccionadas
map("v", "J", ":m '>+1<cr>gv=gv", { desc = "Mover seleccion abajo" })
map("v", "K", ":m '<-2<cr>gv=gv", { desc = "Mover seleccion arriba" })

-- Indentar sin perder la seleccion
map("v", "<", "<gv")
map("v", ">", ">gv")

-- ---------------------------------------------------------------------
-- 6. TIPOS DE ARCHIVO DEVOPS
-- ---------------------------------------------------------------------
vim.filetype.add({
  filename = {
    ["Dockerfile"] = "dockerfile",
    ["docker-compose.yml"] = "yaml",
    ["docker-compose.yaml"] = "yaml",
    ["Jenkinsfile"] = "groovy",
  },
  extension = {
    tf = "terraform",
    tfvars = "terraform",
    hcl = "hcl",
  },
})

vim.api.nvim_create_autocmd("FileType", {
  pattern = { "yaml", "terraform", "hcl", "json", "lua", "sh", "ps1" },
  desc = "Indentacion de 2 espacios para manifiestos e IaC",
  callback = function()
    vim.opt_local.shiftwidth = 2
    vim.opt_local.tabstop = 2
    vim.opt_local.expandtab = true
  end,
})

-- YAML es sensible a la indentacion: mostrarla siempre.
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "yaml" },
  callback = function()
    vim.opt_local.list = true
    vim.opt_local.listchars = { tab = "> ", trail = "~", space = "." }
    vim.opt_local.cursorcolumn = true
  end,
})

-- Resaltar brevemente el texto copiado (util al proyectar en clase).
vim.api.nvim_create_autocmd("TextYankPost", {
  desc = "Destacar el yank",
  callback = function()
    vim.highlight.on_yank({ timeout = 150 })
  end,
})

-- ---------------------------------------------------------------------
-- 7. APARIENCIA
-- ---------------------------------------------------------------------
-- habamax viene incluido en Neovim y combina con el tema tokyo-night de
-- Herdr sin necesidad de instalar plugins.
pcall(vim.cmd.colorscheme, "habamax")

opt.laststatus = 3 -- una sola statusline global, mas limpia en paneles angostos
opt.statusline = "  %f %m%r%=%y  %l:%c  %P  "

-- Explorador netrw en modo arbol y sin banner
vim.g.netrw_banner = 0
vim.g.netrw_liststyle = 3
vim.g.netrw_winsize = 25
