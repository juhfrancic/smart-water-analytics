const map = L.map('map').setView([-21.800, -48.185], 13);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    maxZoom: 19
}).addTo(map);

let chartPerdas = null;
let chartEfic   = null;

// Extrai o nome do bairro removendo o sufixo do tipo de ponto
function extrairBairro(nomePonto) {
    return nomePonto
        .replace(/ Monitoring Node$/, '')
        .replace(/ Pressure Point$/, '')
        .replace(/ Flow Meter$/, '')
        .replace(/ Backup Pressure Point$/, '')
        .replace(/ Secondary Pressure Point$/, '')
        .replace(/ Secondary Flow Meter$/, '')
        .trim();
}

function obterCor(status) {
    if (!status) return '#10b981';
    const s = status.toLowerCase();
    if (s === 'critico' || s.includes('crít') || s === 'critical') return '#ef4444';
    if (s === 'alerta' || s.includes('alert') || s === 'maintenance') return '#f59e0b';
    return '#10b981';
}

function piorStatus(pontos) {
    const ordem = ['critical', 'critico', 'maintenance', 'alerta', 'active', 'normal', 'ativo'];
    let pior = 'active';
    pontos.forEach(function(p) {
        const s = (p.status_operacional || '').toLowerCase();
        if (ordem.indexOf(s) < ordem.indexOf(pior)) pior = s;
    });
    return pior;
}

function aplicarBadge(status) {
    const badge = document.getElementById('badge-status');
    const s = (status || '').toLowerCase();
    if (s === 'active' || s === 'normal' || s === 'ativo') {
        badge.innerText = 'NORMAL';
        badge.className = 'badge status-normal';
    } else if (s === 'maintenance' || s === 'alerta') {
        badge.innerText = 'MANUTENCAO';
        badge.className = 'badge status-alerta';
    } else {
        badge.innerText = 'CRITICO';
        badge.className = 'badge status-critico';
    }
}

function renderPerdas(historico) {
    const ctx = document.getElementById('graficoPerdas').getContext('2d');
    if (chartPerdas) chartPerdas.destroy();
    chartPerdas = new Chart(ctx, {
        type: 'line',
        data: {
            labels: historico.map(function(i) { return i.data; }),
            datasets: [{
                label: 'Perdas (%)',
                data: historico.map(function(i) { return i.percentual_perda; }),
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56,189,248,0.1)',
                borderWidth: 2, fill: true, tension: 0.4,
                pointRadius: 4, pointBackgroundColor: '#38bdf8'
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#94a3b8', maxTicksLimit: 7 }, grid: { color: '#1e293b' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
            }
        }
    });
}

function renderEfic(eficiencia) {
    const canvas = document.getElementById('graficoEficiencia');
    if (!canvas || !eficiencia || eficiencia.length === 0) return;
    const ctx = canvas.getContext('2d');
    if (chartEfic) chartEfic.destroy();
    chartEfic = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: eficiencia.map(function(i) { return i.data; }),
            datasets: [{
                label: 'Eficiencia (%)',
                data: eficiencia.map(function(i) { return i.eficiencia_percentual; }),
                backgroundColor: 'rgba(16,185,129,0.6)',
                borderColor: '#10b981', borderWidth: 1, borderRadius: 4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
                y: { min: 0, max: 100, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
            }
        }
    });
}

function renderAlertas(alertas) {
    const c = document.getElementById('alertas-container');
    if (!c) return;
    c.innerHTML = '';
    if (!alertas || alertas.length === 0) {
        c.innerHTML = '<div class="alerta-item alerta-ok">Sem alertas ativos neste ponto</div>';
        return;
    }
    alertas.forEach(function(a) {
        const sev = (a.severidade || '').toLowerCase();
        const cls = sev.includes('high') || sev.includes('crít') || sev.includes('alta') ? 'alerta-critico'
                  : sev.includes('med') ? 'alerta-alerta' : 'alerta-ok';
        const div = document.createElement('div');
        div.className = 'alerta-item ' + cls;
        div.innerHTML = '<strong>' + (a.tipo_alerta || '') + '</strong> — ' + (a.severidade || '') + '<br>'
            + '<span>' + (a.descricao || '') + '</span><br>'
            + '<small>Equipe: ' + (a.equipe_responsavel || '-') + '</small>';
        c.appendChild(div);
    });
}

function renderManutencoes(lista) {
    const c = document.getElementById('manutencoes-container');
    if (!c) return;
    c.innerHTML = '';
    if (!lista || lista.length === 0) {
        c.innerHTML = '<p style="color:#64748b;font-size:0.8rem;">Nenhuma manutencao recente.</p>';
        return;
    }
    lista.forEach(function(m) {
        const div = document.createElement('div');
        div.className = 'manutencao-item';
        div.innerHTML = '<strong>' + (m.tipo_manutencao || '') + '</strong> — ' + (m.status_manutencao || '') + '<br>'
            + '<span>' + (m.descricao_manutencao || '') + '</span><br>'
            + '<small>Equipe: ' + (m.equipe_tecnica || '-') + ' | Clientes: ' + (m.clientes_afetados || 0) + '</small>';
        c.appendChild(div);
    });
}

// Renderiza mini-tabela com os sub-pontos do bairro
function renderSubpontos(pontos) {
    let c = document.getElementById('subpontos-container');
    if (!c) return;
    c.innerHTML = '';
    pontos.forEach(function(p) {
        const tipo = p.nome_ponto.replace(extrairBairro(p.nome_ponto), '').trim() || p.tipo_ponto || '-';
        const div = document.createElement('div');
        div.className = 'subponto-item';
        div.innerHTML = '<span class="subponto-tipo">' + tipo + '</span>'
            + (p.pressao_atual != null ? ' <span class="subponto-val">' + p.pressao_atual.toFixed(3) + ' MPa</span>' : '')
            + (p.vazao_atual   != null ? ' <span class="subponto-val">' + p.vazao_atual.toFixed(1)   + ' L/m</span>'  : '')
            + (p.nivel_atual   != null ? ' <span class="subponto-val">' + p.nivel_atual.toFixed(1)   + ' %</span>'   : '');
        c.appendChild(div);
    });
}

async function selecionarBairro(nomeBairro, pontos, status) {
    document.getElementById('txt-nome-ponto').innerText = nomeBairro;
    aplicarBadge(status);

    // Usa o primeiro ponto com dados como referência para telemetria e gráficos
    const pontoPrincipal = pontos.find(function(p) { return p.pressao_atual != null; }) || pontos[0];

    // KPIs: média dos pontos com dados
    const comPressao = pontos.filter(function(p) { return p.pressao_atual != null; });
    const comVazao   = pontos.filter(function(p) { return p.vazao_atual   != null; });
    const comNivel   = pontos.filter(function(p) { return p.nivel_atual   != null; });

    const media = function(arr, campo) {
        if (!arr.length) return null;
        return arr.reduce(function(s, p) { return s + p[campo]; }, 0) / arr.length;
    };

    const pressao = media(comPressao, 'pressao_atual');
    const vazao   = media(comVazao,   'vazao_atual');
    const nivel   = media(comNivel,   'nivel_atual');

    document.getElementById('kpi-pressao').innerHTML =
        pressao != null ? pressao.toFixed(3) + ' <span class="unit">MPa</span>' : '-- <span class="unit">MPa</span>';
    document.getElementById('kpi-vazao').innerHTML =
        vazao != null ? vazao.toFixed(1) + ' <span class="unit">L/m</span>' : '-- <span class="unit">L/m</span>';
    document.getElementById('kpi-nivel').innerHTML =
        nivel != null ? nivel.toFixed(1) + ' <span class="unit">%</span>' : '-- <span class="unit">%</span>';

    renderSubpontos(pontos);

    // Busca histórico e alertas pelo ponto principal
    try {
        const resp  = await fetch('/api/dados/' + pontoPrincipal.ponto_rede_id);
        const dados = await resp.json();
        if (dados.historico_perdas && dados.historico_perdas.length > 0) renderPerdas(dados.historico_perdas);
        if (dados.eficiencia       && dados.eficiencia.length > 0)       renderEfic(dados.eficiencia);
        renderAlertas(dados.alertas);
        renderManutencoes(dados.manutencoes);
    } catch(e) {
        console.error('Erro:', e);
    }
}

async function inicializarMapa() {
    console.log('Carregando pontos...');
    try {
        const resp   = await fetch('/api/pontos');
        const pontos = await resp.json();
        console.log('Total de pontos:', pontos.length);

        // Agrupa por bairro
        const bairros = {};
        pontos.forEach(function(p) {
            const bairro = extrairBairro(p.nome_ponto);
            if (!bairros[bairro]) bairros[bairro] = [];
            bairros[bairro].push(p);
        });

        console.log('Bairros:', Object.keys(bairros).length);

        Object.keys(bairros).forEach(function(nomeBairro) {
            const grupo = bairros[nomeBairro];

            // Coordenada central do bairro (média do grupo)
            const lat = grupo.reduce(function(s, p) { return s + p.latitude;  }, 0) / grupo.length;
            const lng = grupo.reduce(function(s, p) { return s + p.longitude; }, 0) / grupo.length;

            const status = piorStatus(grupo);

            const marker = L.circleMarker([lat, lng], {
                radius: 11,
                fillColor: obterCor(status),
                color: '#fff',
                weight: 2,
                fillOpacity: 0.9
            }).addTo(map);

            // Tooltip mostra bairro e quantos sub-pontos
            const comDados = grupo.filter(function(p) { return p.pressao_atual != null; });
            const pressaoMedia = comDados.length
                ? (comDados.reduce(function(s,p){return s+p.pressao_atual;},0)/comDados.length).toFixed(3)
                : null;

            const tooltip = '<b>' + nomeBairro + '</b><br>'
                + grupo.length + ' pontos monitorados'
                + (pressaoMedia ? '<br>P média: ' + pressaoMedia + ' MPa' : '');

            marker.bindTooltip(tooltip, { direction: 'top', offset: [0, -10] });
            marker.on('click', function() {
                selecionarBairro(nomeBairro, grupo, status);
            });
        });

        console.log('Mapa carregado!');
    } catch(e) {
        console.error('Erro ao carregar mapa:', e);
    }
}

inicializarMapa();