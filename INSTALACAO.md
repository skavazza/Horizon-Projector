# INSTALAÇÃO RÁPIDA - Horizon Projector Plugin QGIS

## 🎯 Passo a Passo Simplificado

### 1. Localize a Pasta de Plugins do QGIS

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

### 2. Crie a Pasta do Plugin

Dentro da pasta de plugins, crie uma pasta chamada: `horizon`

### 3. Copie os Arquivos

Copie TODOS os seguintes arquivos para dentro da pasta `horizon`:

✅ **Arquivos Obrigatórios:**
- `horizon.py`
- `horizon_dialog.py`
- `horizon_dialog_base.ui`
- `metadata.txt`
- `__init__.py` (criar se não existir)

✅ **Arquivos Opcionais mas Recomendados:**
- `resources.py` (ou `resources.qrc`)
- `icon.png`
- `README.md`

### 4. Criar __init__.py

Se não tiver o arquivo `__init__.py`, crie-o com o seguinte conteúdo:

```python
# -*- coding: utf-8 -*-

def classFactory(iface):
    from .horizon import horizon
    return horizon(iface)
```

### 5. Gerar resources.py (Opcional)

Se você tiver um arquivo `resources.qrc`, execute:

```bash
pyrcc5 -o resources.py resources.qrc
```

Se não tiver, crie um `resources.py` vazio:

```python
# -*- coding: utf-8 -*-
# Resource object code (empty)
```

### 6. Reiniciar o QGIS

Feche completamente o QGIS e abra novamente.

### 7. Ativar o Plugin

1. No QGIS, vá em: **Plugins → Gerenciar e instalar plugins**
2. Clique na aba **Instalados**
3. Procure por **Horizon Projector**
4. Marque a caixa ao lado para ativar
5. Clique em **Fechar**

### 8. Usar o Plugin

O plugin estará disponível em:
- **Menu**: `Plugins → Horizon Projector`
- **Barra de ferramentas**: Procure pelo ícone do plugin

## 🔧 Estrutura de Arquivos Final

```
plugins/
└── horizon/
    ├── __init__.py
    ├── horizon.py
    ├── horizon_dialog.py
    ├── horizon_dialog_base.ui
    ├── metadata.txt
    ├── resources.py (opcional)
    ├── icon.png (opcional)
    └── README.md (opcional)
```

## ❓ Problemas Comuns

### Plugin não aparece na lista
- Verifique se a pasta se chama exatamente `horizon` (minúsculo)
- Verifique se o arquivo `__init__.py` existe
- Reinicie o QGIS completamente

### Erro ao carregar o plugin
- Abra: **Plugins → Console Python**
- Digite: `import horizon`
- Veja a mensagem de erro para diagnosticar

### Plugin aparece mas não funciona
- Verifique se todos os arquivos `.py` estão na pasta
- Verifique se o arquivo `.ui` está presente
- Verifique permissões dos arquivos

## 📞 Precisa de Ajuda?

1. Verifique o arquivo `README.md` completo
2. Confira os logs do QGIS em: **View → Panels → Log Messages**
3. Entre em contato: betorodriuges@msn.com

---

**Boa sorte com seu Horizon Projector! 🚀**
