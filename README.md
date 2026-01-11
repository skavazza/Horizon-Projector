# Horizon Projector - Plugin QGIS

Plugin QGIS para cálculo de distâncias ao horizonte, objetos visíveis e projeções geodésicas. Ideal para navegação marítima, geodésia e aplicações náuticas.

## 📋 Recursos Principais

### 1️⃣ **Cálculo de Horizonte**
- Calcula a distância ao horizonte baseado na altura do observador
- Fórmula: `d = sqrt(2 * R * h + h²)`
- Exibe resultados em km e milhas náuticas (NM)
- Desenha círculo do horizonte no mapa QGIS

### 2️⃣ **Objeto Visível**
- Calcula distância máxima para visualizar objetos
- Considera altura do observador e do objeto
- Útil para faróis, torres, montanhas, etc.
- Desenha círculo de visibilidade no mapa

### 3️⃣ **Projeção Geodésica**
- Projeta coordenadas via azimute magnético e distância
- Correção automática com declinação magnética
- Calcula azimute verdadeiro
- Desenha linha e pontos no mapa

### 4️⃣ **Anéis de Distância**
- Cria anéis concêntricos em intervalos configuráveis
- Padrão: Milhas Náuticas (NM)
- Gradiente de cores (verde → vermelho)
- Etiquetas automáticas com distâncias

### 5️⃣ **Exportação**
- GPX (GPS Exchange Format)
- KML (Keyhole Markup Language)
- Shapefile
- GeoJSON

## 🚀 Instalação

### Método 1: Instalação Manual

1. **Baixe os arquivos do plugin**:
   - `horizon.py`
   - `horizon_dialog.py`
   - `horizon_dialog_base.ui`
   - `resources.py` (gerado pelo pyrcc5)
   - `metadata.txt`
   - `icon.png`

2. **Localize o diretório de plugins do QGIS**:
   
   **Windows:**
   ```
   C:\Users\[SeuUsuário]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
   ```
   
   **Linux:**
   ```
   ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
   ```
   
   **macOS:**
   ```
   ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
   ```

3. **Crie uma pasta chamada `horizon`** no diretório de plugins

4. **Copie todos os arquivos** para dentro da pasta `horizon`

5. **Reinicie o QGIS**

6. **Ative o plugin**:
   - Vá em `Plugins → Gerenciar e instalar plugins`
   - Aba `Instalados`
   - Marque a caixa `Horizon Projector`

### Método 2: Via ZIP (se disponível)

1. Baixe o arquivo `.zip` do plugin
2. No QGIS: `Plugins → Gerenciar e instalar plugins`
3. Aba `Instalar a partir do ZIP`
4. Selecione o arquivo e clique `Instalar Plugin`

## 📖 Como Usar

### Abertura do Plugin

Após ativação, o plugin estará disponível em:
- **Menu**: `Plugins → Horizon Projector`
- **Barra de ferramentas**: Ícone do Horizon Projector

### Aba 1: Horizonte

1. **Definir Coordenadas**:
   - Insira latitude e longitude manualmente, OU
   - Clique em "Usar Centro do Canvas" para usar o centro atual do mapa, OU
   - Clique em "Usar Abrolhos (Default)" para Abrolhos, BA (-17.5392, -39.7277)

2. **Definir Altura**:
   - Insira a altura do observador em metros (ex: 1.7m para pessoa, 10m para embarcação)

3. **Calcular**:
   - Clique em "Calcular Distância ao Horizonte"
   - Resultados aparecem em km e NM

4. **Visualizar**:
   - Clique em "Desenhar Círculo no Mapa"
   - Um círculo ciano será desenhado representando o horizonte
   - Um ponto marcará a posição do observador

### Aba 2: Objeto Visível

1. **Definir Coordenadas** do observador

2. **Definir Alturas**:
   - Altura do observador (m)
   - Altura do objeto que deseja visualizar (m)

3. **Calcular**:
   - Clique em "Calcular Distância do Objeto"
   - Mostra a distância máxima para visualização

4. **Visualizar**:
   - Círculo laranja tracejado mostra o alcance

### Aba 3: Projeção

1. **Ponto de Partida**: Defina coordenadas iniciais

2. **Parâmetros de Projeção**:
   - **Azimute Magnético**: Direção da bússola (0-360°)
   - **Distância**: Distância a projetar (km)
   - **Elevação**: Elevação do ponto (opcional)
   - **Declinação Magnética**: Padrão -23.933° (Abrolhos)

3. **Calcular**:
   - Obtém coordenadas do alvo e azimute verdadeiro

4. **Visualizar**:
   - Linha tracejada laranja do ponto inicial ao alvo
   - Pontos marcando origem e destino

### Aba 4: Anéis de Distância

1. **Centro dos Anéis**: Defina coordenadas centrais

2. **Configurações**:
   - **Número de Anéis**: Quantidade (1-50)
   - **Intervalo**: Distância entre anéis em NM
   - **Mostrar Etiquetas**: Exibe distâncias
   - **Gradiente de Cores**: Verde (perto) → Vermelho (longe)

3. **Desenhar**:
   - Cria anéis concêntricos perfeitos para navegação

### Aba 5: Exportar

- **Exportar GPX**: Para dispositivos GPS (apenas pontos)
- **Exportar KML**: Para Google Earth
- **Exportar Shapefile**: Para análise GIS
- **Exportar GeoJSON**: Para web mapping
- **Limpar Camadas**: Remove todas as camadas criadas

## 🧮 Fórmulas e Cálculos

### Distância ao Horizonte
```
d = √(2 × R × h + h²)
```
Onde:
- `d` = distância ao horizonte (km)
- `R` = raio da Terra (6371 km)
- `h` = altura do observador (km)

### Distância de Objeto Visível
```
d_total = d_observador + d_objeto
```
Soma das distâncias ao horizonte do observador e do objeto.

### Projeção Geodésica
Utiliza a fórmula **haversine** para cálculo preciso:
```
lat2 = asin(sin(lat1) × cos(δ) + cos(lat1) × sin(δ) × cos(θ))
lon2 = lon1 + atan2(sin(θ) × sin(δ) × cos(lat1), cos(δ) - sin(lat1) × sin(lat2))
```
Onde:
- `δ` = distância angular (distância / raio da Terra)
- `θ` = azimute em radianos

## 🌍 Aplicações Práticas

### Navegação Marítima
- Calcular alcance visual de faróis
- Planejar rotas com visibilidade de pontos de referência
- Determinar quando objetos aparecerão no horizonte

### Geodésia e Topografia
- Estudos de linha de visada
- Planejamento de torres de comunicação
- Análise de intervisibilidade

### Busca e Resgate
- Calcular área de busca visual
- Determinar raio de cobertura de observadores
- Planejamento de posicionamento de equipes

### Fotografia e Observação
- Planejamento de locais para fotografia
- Observação de estrelas e astronomia
- Estudos de paisagem e geografia

## ⚙️ Configurações Padrão

- **Raio da Terra**: 6371 km
- **Declinação Magnética (Abrolhos)**: -23.933°
- **Coordenadas Padrão**: Abrolhos, BA (-17.5392, -39.7277)
- **Conversão**: 1 NM = 1.852 km = 1852 m
- **Sistema de Referência**: EPSG:4326 (WGS84)

## 🎨 Cores das Camadas

- **Ciano (#00FFF5)**: Horizonte do observador
- **Laranja (#FF6B35)**: Objetos e projeções
- **Gradiente Verde→Vermelho**: Anéis de distância

## 🔧 Requisitos

- **QGIS**: Versão 3.0 ou superior
- **Python**: 3.6+
- **Bibliotecas Python**: `math` (padrão)
- **Qt**: PyQt5 (incluído no QGIS)

## 📝 Notas Importantes

1. **Curvatura da Terra**: Todos os cálculos consideram a curvatura terrestre
2. **Precisão**: Fórmulas geodésicas precisas (haversine) para grandes distâncias
3. **Declinação Magnética**: Ajuste conforme sua localização (use NOAA/IGRF)
4. **Unidades**: Sempre especifique unidades corretas (m, km, NM)
5. **CRS**: Todas as camadas são criadas em EPSG:4326 (WGS84)

## 🐛 Solução de Problemas

### Plugin não aparece no menu
- Verifique se está ativado em `Gerenciar e instalar plugins`
- Reinicie o QGIS
- Verifique se todos os arquivos estão na pasta correta

### Erros ao desenhar no mapa
- Verifique se há um projeto aberto
- Certifique-se de que o CRS do projeto é compatível
- Tente recarregar o plugin

### Resultados inesperados
- Verifique as unidades (m vs km, graus vs radianos)
- Confirme a declinação magnética para sua área
- Valide as coordenadas de entrada

## 📄 Licença

GNU General Public License v2.0 ou superior

## 👤 Autor

**Alberto Rodrigues**
- Email: betorodriuges@msn.com
- Data: 2026-01-11

## 🙏 Agradecimentos

Baseado no conceito do **Horizon Projector** web application.

## 📚 Referências

- [QGIS Plugin Development](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)
- [Great Circle Navigation](https://en.wikipedia.org/wiki/Great-circle_navigation)
- [NOAA Magnetic Declination](https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml)

## 🔄 Atualizações Futuras

- [ ] Integração com modelos de elevação (DEM)
- [ ] Cálculo automático de declinação magnética via API
- [ ] Suporte para diferentes modelos de Terra (WGS84, GRS80)
- [ ] Análise de perfil de elevação
- [ ] Banco de dados de faróis e navegação
- [ ] Integração com dados meteorológicos
- [ ] Modo 3D com visualização de terreno

---

**Versão**: 1.0  
**Última Atualização**: Janeiro 2026
