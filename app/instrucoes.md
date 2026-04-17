# 💧 Guia Oficial de Desenvolvimento — SmartWater (Grupo 6)

Bem-vindos ao projeto **SmartWater**! Nosso objetivo é entregar um software de nível profissional, atuando não apenas como um site, mas como um **Aplicativo Mobile real (.apk)** integrado a uma API inteligente e ao Dashboard da equipe de infraestrutura (Grupo 5).

Este é o nosso manual definitivo: como a arquitetura funciona, como configurar o ambiente e como vamos trabalhar juntos sem ninguém perder código ou travar o PC.

---

## 🏗️ 1. A Arquitetura: como o site vira App?

Nosso projeto usa uma arquitetura de **Monorepo** (tudo no mesmo repositório do GitHub), dividido em duas grandes áreas:

**🐍 `app/backend/` (O Motor):** Feito em Python (Flask) e MySQL. É aqui que ficam as regras de negócio, rotas da API, alertas de vazamento e conexão com os hardwares. O código daqui roda no servidor/nuvem.

**📱 `app/frontend/` (A Interface e o App):** Feito em HTML, TailwindCSS e JavaScript.

**O pulo do gato:** usamos uma tecnologia chamada **Capacitor**. Ela pega todo o nosso código de site (HTML/CSS) e empacota dentro de um aplicativo Android nativo.

**Onde programar?** A galera do Front-end vai criar os arquivos `index.html` e os estilos **exclusivamente dentro da pasta `app/frontend/www/`**. É essa pasta que o Capacitor lê para gerar o app.

---

## 🛠️ 2. O que você precisa instalar no seu PC

Antes de baixar o código, garanta que seu computador tem as ferramentas de trabalho:

- **VS Code** — Nosso editor oficial. Instale a extensão **Live Server** para testar o front-end na hora.
- **Git** — Para baixar e enviar código para o GitHub.
- **Node.js (versão 22 LTS ou superior)** — Obrigatório para o time de Front-end compilar o Tailwind e gerar o App.
- **Python 3.10+** — Obrigatório para o time de Back-end.
- **XAMPP ou MySQL Server** — Para o banco de dados local.
- **Android Studio** (apenas Tech Lead / Front) — Para compilar a versão final do `.apk`.

---

## 🚀 3. Como rodar o projeto pela 1ª vez

Abra o terminal na pasta onde deseja salvar o projeto e baixe o código:

```bash
git clone https://github.com/SEU-USUARIO/smartwater-app.git
cd smartwater-app
```

### 🐍 Se você é da equipe de Back-end (Python)

Toda vez que você abrir o projeto para trabalhar no código Python, você precisa garantir que a `venv` (ambiente virtual) está ativa. Siga o passo a passo abaixo **rigorosamente** para evitar erros de versão ou de permissão.

**Primeiro acesso (Setup Inicial):**

1. Abra o PowerShell na pasta `app/backend`.
2. Libere a execução de scripts (só precisa fazer uma vez no PC):

   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. Crie o ambiente virtual:

   ```powershell
   python -m venv venv
   ```

4. Ative a venv e instale as dependências:

   ```powershell
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

   > No Linux/Mac, a ativação é: `source venv/bin/activate`

**Rotina diária (como iniciar o trabalho):**

1. Navegue até `app/backend`.
2. Ative a venv: `.\venv\Scripts\activate`
   - **Dica:** você saberá que deu certo se aparecer `(venv)` no início da linha do terminal.
3. Inicie a API: `python app.py` — ela roda em `http://localhost:5000`.

### 🎨 Se você é da equipe de Front-end (UI/UX)

O frontend utiliza **TailwindCSS** para o visual e **Capacitor** para transformar o site em aplicativo Android.

1. Navegue até `app/frontend`.
2. Instale as ferramentas (Tailwind, Capacitor e afins):

   ```bash
   npm install
   ```

3. **Para programar o layout e ver no PC (Web):** abra a pasta `app/frontend/www/` no VS Code, clique com o botão direito no `index.html` e escolha **"Open with Live Server"**. O site abre no navegador e atualiza sozinho a cada modificação.

4. **Para compilar o Tailwind:** mantenha um terminal aberto rodando:

   ```bash
   npx tailwindcss -i ./src/input.css -o ./www/output.css --watch
   ```

   O Tech Lead ajuda a configurar esse script final.

---

## 🛡️ 4. O Fluxo de Trabalho no GitHub (MUITO IMPORTANTE)

**Regra de Ouro Inquebrável:** é **PROIBIDO** enviar código direto para a branch `main`. A `main` é sagrada e representa o produto que vai para a apresentação — por isso ela está **bloqueada**.

Seja para fazer uma tela nova ou criar uma tabela no banco, siga sempre esta rotina diária:

**Passo 1 — Atualize seu código antes de começar o dia:**

```bash
git checkout main
git pull origin main
```

**Passo 2 — Crie a sua área de rascunho (branch):**

```bash
# Exemplo front: git checkout -b front/tela-login
# Exemplo back:  git checkout -b back/rota-sensores
git checkout -b <sua-equipe>/<nome-da-tarefa>
```

**Passo 3 — Salve seu trabalho (commit):**

```bash
git add .
git commit -m "Cria a tela de login do morador"
```

**Passo 4 — Envie para o GitHub e peça aprovação (Pull Request):**

```bash
git push origin <sua-equipe>/<nome-da-tarefa>
```

Vá até a página do repositório no navegador, clique no botão verde **"Compare & pull request"**. O Tech Lead faz a revisão do código; se estiver tudo rodando bem, ele une o seu código à `main`.

---

## 📱 5. Geração do Aplicativo Android (Front-end / Tech Lead)

Toda vez que a equipe de UI terminar uma tela nova dentro da pasta `www/`, precisamos avisar o aplicativo Android que há código novo.

No terminal, dentro da pasta `app/frontend`:

```bash
npx cap sync android
```

Isso copia todo o HTML/CSS da pasta `www` para dentro do código do app Android.

Para testar no emulador ou gerar o instalador (`.apk`):

```bash
npx cap open android
```

Isso abre o Android Studio já configurado.

---

## 🤝 6. Integração com o Grupo 5 (Infraestrutura / Dashboards)

O Grupo 5 deve trabalhar em uma pasta combinada no monorepo **ou** fornecer o link do dashboard externo.

- **Se for via link:** o desenvolvedor de Front-end deve atualizar o `src` do `<iframe>` na página do Síndico.
- **Se houver arquivos de script deles:** devem ser colocados em uma pasta organizada dentro de `app/`.

---

> **Em caso de dúvidas, erros vermelhos estranhos no terminal ou conflitos de código: pare o que está fazendo e chame o Tech Lead!**
>
> Bom desenvolvimento a todos! 🚀
