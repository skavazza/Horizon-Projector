# -*- coding: utf-8 -*-
"""
/***************************************************************************
 horizonDialog
                                 A QGIS plugin
 Horizon Projector - Cálculo de horizontes, objetos visíveis e projeções
                             -------------------
        begin                : 2026-01-11
        git sha              : $Format:%H$
        copyright            : (C) 2026 by Alberto Rodrigues
        email                : betorodriuges@msn.com
 ***************************************************************************/
"""

import os
import math
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, 
    QgsPointXY, QgsField, QgsFields, QgsCoordinateReferenceSystem,
    QgsMarkerSymbol, QgsLineSymbol, QgsFillSymbol,
    QgsSingleSymbolRenderer, QgsVectorFileWriter, QgsWkbTypes
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'horizon_dialog_base.ui'))


class horizonDialog(QDialog, FORM_CLASS):
    """Dialog principal do Horizon Projector"""
    
    # Constantes
    RAIO_TERRA = 6371.0  # km
    ABROLHOS_LAT = -17.9647
    ABROLHOS_LNG = -38.6941
    NM_TO_KM = 1.852
    NM_TO_M = 1852.0
    
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(horizonDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        
        # Lista para rastrear camadas criadas
        self.created_layers = []
        
        # Conectar sinais dos botões
        self.connect_signals()
        
    def connect_signals(self):
        """Conecta todos os sinais dos botões aos seus slots"""
        # Tab Horizonte
        self.btnUsarCanvas.clicked.connect(self.usar_centro_canvas)
        self.btnUsarAbrolhos.clicked.connect(self.usar_abrolhos)
        self.btnCalcularHorizonte.clicked.connect(self.calcular_horizonte)
        self.btnDesenharHorizonte.clicked.connect(self.desenhar_horizonte)
        
        # Tab Objeto
        self.btnCalcularObjeto.clicked.connect(self.calcular_objeto)
        self.btnDesenharObjeto.clicked.connect(self.desenhar_objeto)
        
        # Tab Projeção
        self.btnCalcularProjecao.clicked.connect(self.calcular_projecao)
        self.btnDesenharProjecao.clicked.connect(self.desenhar_projecao)
        
        # Tab Anéis
        self.btnDesenharAneis.clicked.connect(self.desenhar_aneis)
        
        # Tab Exportar
        self.btnExportarGPX.clicked.connect(self.exportar_gpx)
        self.btnExportarKML.clicked.connect(self.exportar_kml)
        self.btnExportarShapefile.clicked.connect(self.exportar_shapefile)
        self.btnExportarJSON.clicked.connect(self.exportar_geojson)
        self.btnLimparCamadas.clicked.connect(self.limpar_camadas)
    
    # ============ FUNÇÕES DE CÁLCULO ============
    
    def calcular_distancia_horizonte(self, altura_m):
        """
        Calcula a distância ao horizonte baseado na altura do observador.
        Fórmula: d = sqrt(2 * R * h + h²)
        onde R é o raio da Terra em km e h é a altura em km
        """
        h_km = altura_m / 1000.0
        distancia_km = math.sqrt(2 * self.RAIO_TERRA * h_km + h_km * h_km)
        return distancia_km
    
    def calcular_distancia_objeto(self, altura_obs_m, altura_obj_m):
        """
        Calcula a distância máxima para ver um objeto.
        É a soma das distâncias ao horizonte do observador e do objeto.
        """
        dist_obs = self.calcular_distancia_horizonte(altura_obs_m)
        dist_obj = self.calcular_distancia_horizonte(altura_obj_m)
        return dist_obs + dist_obj
    
    def calcular_ponto_destino(self, lat, lon, azimute_verdadeiro, distancia_km):
        """
        Calcula um ponto destino dado um ponto inicial, azimute e distância.
        Usa a fórmula haversine para cálculo preciso.
        
        Args:
            lat: Latitude inicial em graus
            lon: Longitude inicial em graus
            azimute_verdadeiro: Azimute em graus (0-360)
            distancia_km: Distância em quilômetros
        
        Returns:
            Tupla (lat_destino, lon_destino)
        """
        # Converter para radianos
        lat1 = math.radians(lat)
        lon1 = math.radians(lon)
        brng = math.radians(azimute_verdadeiro)
        
        # Distância angular (distância / raio da Terra)
        dist_angular = distancia_km / self.RAIO_TERRA
        
        # Calcular nova latitude
        lat2 = math.asin(
            math.sin(lat1) * math.cos(dist_angular) +
            math.cos(lat1) * math.sin(dist_angular) * math.cos(brng)
        )
        
        # Calcular nova longitude
        lon2 = lon1 + math.atan2(
            math.sin(brng) * math.sin(dist_angular) * math.cos(lat1),
            math.cos(dist_angular) - math.sin(lat1) * math.sin(lat2)
        )
        
        # Converter de volta para graus
        lat_dest = math.degrees(lat2)
        lon_dest = math.degrees(lon2)
        
        return lat_dest, lon_dest
    
    # ============ SLOTS - TAB HORIZONTE ============
    
    def usar_centro_canvas(self):
        """Usa o centro do canvas atual para as coordenadas"""
        extent = self.canvas.extent()
        centro = extent.center()
        
        # Atualizar todos os spin boxes de latitude/longitude
        self.spinLatitude.setValue(centro.y())
        self.spinLongitude.setValue(centro.x())
        self.spinLatitudeObj.setValue(centro.y())
        self.spinLongitudeObj.setValue(centro.x())
        self.spinLatitudeProj.setValue(centro.y())
        self.spinLongitudeProj.setValue(centro.x())
        self.spinLatitudeAneis.setValue(centro.y())
        self.spinLongitudeAneis.setValue(centro.x())
        
        QMessageBox.information(self, "Sucesso", 
            f"Coordenadas atualizadas:\nLat: {centro.y():.6f}\nLng: {centro.x():.6f}")
    
    def usar_abrolhos(self):
        """Define as coordenadas padrão de Abrolhos"""
        self.spinLatitude.setValue(self.ABROLHOS_LAT)
        self.spinLongitude.setValue(self.ABROLHOS_LNG)
        self.spinLatitudeObj.setValue(self.ABROLHOS_LAT)
        self.spinLongitudeObj.setValue(self.ABROLHOS_LNG)
        self.spinLatitudeProj.setValue(self.ABROLHOS_LAT)
        self.spinLongitudeProj.setValue(self.ABROLHOS_LNG)
        self.spinLatitudeAneis.setValue(self.ABROLHOS_LAT)
        self.spinLongitudeAneis.setValue(self.ABROLHOS_LNG)
        
        QMessageBox.information(self, "Sucesso", 
            "Coordenadas de Abrolhos (BA) aplicadas")
    
    def calcular_horizonte(self):
        """Calcula a distância ao horizonte"""
        altura = self.spinAlturaObservador.value()
        
        distancia_km = self.calcular_distancia_horizonte(altura)
        distancia_nm = distancia_km / self.NM_TO_KM
        
        self.txtDistHorizonte.setText(f"{distancia_km:.2f} km")
        self.txtDistNM.setText(f"{distancia_nm:.2f} NM")
        
        QMessageBox.information(self, "Resultado", 
            f"Distância ao horizonte: {distancia_km:.2f} km ({distancia_nm:.2f} NM)")
    
    def desenhar_horizonte(self):
        """Desenha o círculo do horizonte no mapa"""
        lat = self.spinLatitude.value()
        lon = self.spinLongitude.value()
        altura = self.spinAlturaObservador.value()
        
        distancia_km = self.calcular_distancia_horizonte(altura)
        
        # Criar camada de memória
        layer = QgsVectorLayer("Polygon?crs=EPSG:4326", 
                               f"Horizonte ({distancia_km:.2f} km)", "memory")
        provider = layer.dataProvider()
        
        # Adicionar campos
        provider.addAttributes([
            QgsField("tipo", QVariant.String),
            QgsField("distancia_km", QVariant.Double),
            QgsField("distancia_nm", QVariant.Double),
            QgsField("altura_obs_m", QVariant.Double)
        ])
        layer.updateFields()
        
        # Criar círculo (buffer ao redor do ponto)
        centro = QgsPointXY(lon, lat)
        # Aproximação: 1 grau ≈ 111 km
        raio_graus = distancia_km / 111.0
        
        # Criar polígono circular
        pontos = []
        num_pontos = 64
        for i in range(num_pontos + 1):
            angulo = (360.0 / num_pontos) * i
            rad = math.radians(angulo)
            x = lon + raio_graus * math.cos(rad)
            y = lat + raio_graus * math.sin(rad)
            pontos.append(QgsPointXY(x, y))
        
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolygonXY([pontos]))
        feature.setAttributes([
            "horizonte",
            distancia_km,
            distancia_km / self.NM_TO_KM,
            altura
        ])
        
        provider.addFeature(feature)
        layer.updateExtents()
        
        # Estilizar
        symbol = QgsFillSymbol.createSimple({
            'color': '0,255,245,30',
            'outline_color': '0,255,245',
            'outline_width': '0.5'
        })
        layer.renderer().setSymbol(symbol)
        
        # Adicionar ponto central
        point_layer = QgsVectorLayer("Point?crs=EPSG:4326", 
                                     "Observador", "memory")
        point_provider = point_layer.dataProvider()
        point_provider.addAttributes([
            QgsField("tipo", QVariant.String),
            QgsField("lat", QVariant.Double),
            QgsField("lon", QVariant.Double)
        ])
        point_layer.updateFields()
        
        point_feature = QgsFeature()
        point_feature.setGeometry(QgsGeometry.fromPointXY(centro))
        point_feature.setAttributes(["observador", lat, lon])
        point_provider.addFeature(point_feature)
        
        point_symbol = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '0,255,245',
            'size': '3',
            'outline_color': 'white',
            'outline_width': '0.5'
        })
        point_layer.renderer().setSymbol(point_symbol)
        
        # Adicionar ao projeto
        QgsProject.instance().addMapLayer(layer)
        QgsProject.instance().addMapLayer(point_layer)
        
        self.created_layers.append(layer)
        self.created_layers.append(point_layer)
        
        # Zoom para a camada
        self.canvas.setExtent(layer.extent())
        self.canvas.refresh()
        
        QMessageBox.information(self, "Sucesso", 
            "Círculo do horizonte desenhado no mapa!")
    
    # ============ SLOTS - TAB OBJETO ============
    
    def calcular_objeto(self):
        """Calcula a distância até um objeto visível"""
        altura_obs = self.spinAlturaObservadorObj.value()
        altura_obj = self.spinAlturaObjeto.value()
        
        distancia_km = self.calcular_distancia_objeto(altura_obs, altura_obj)
        distancia_nm = distancia_km / self.NM_TO_KM
        
        self.txtDistObjeto.setText(f"{distancia_km:.2f} km")
        self.txtDistObjetoNM.setText(f"{distancia_nm:.2f} NM")
        
        QMessageBox.information(self, "Resultado", 
            f"Distância até objeto: {distancia_km:.2f} km ({distancia_nm:.2f} NM)")
    
    def desenhar_objeto(self):
        """Desenha o círculo do objeto visível no mapa"""
        lat = self.spinLatitudeObj.value()
        lon = self.spinLongitudeObj.value()
        altura_obs = self.spinAlturaObservadorObj.value()
        altura_obj = self.spinAlturaObjeto.value()
        
        distancia_km = self.calcular_distancia_objeto(altura_obs, altura_obj)
        
        # Criar camada
        layer = QgsVectorLayer("Polygon?crs=EPSG:4326", 
                               f"Objeto Visível ({distancia_km:.2f} km)", "memory")
        provider = layer.dataProvider()
        
        provider.addAttributes([
            QgsField("tipo", QVariant.String),
            QgsField("distancia_km", QVariant.Double),
            QgsField("altura_obs_m", QVariant.Double),
            QgsField("altura_obj_m", QVariant.Double)
        ])
        layer.updateFields()
        
        # Criar círculo
        centro = QgsPointXY(lon, lat)
        raio_graus = distancia_km / 111.0
        
        pontos = []
        num_pontos = 64
        for i in range(num_pontos + 1):
            angulo = (360.0 / num_pontos) * i
            rad = math.radians(angulo)
            x = lon + raio_graus * math.cos(rad)
            y = lat + raio_graus * math.sin(rad)
            pontos.append(QgsPointXY(x, y))
        
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolygonXY([pontos]))
        feature.setAttributes([
            "objeto_visivel",
            distancia_km,
            altura_obs,
            altura_obj
        ])
        
        provider.addFeature(feature)
        layer.updateExtents()
        
        # Estilizar com cor laranja
        symbol = QgsFillSymbol.createSimple({
            'color': '255,107,53,30',
            'outline_color': '255,107,53',
            'outline_width': '0.5',
            'outline_style': 'dash'
        })
        layer.renderer().setSymbol(symbol)
        
        # Adicionar ao projeto
        QgsProject.instance().addMapLayer(layer)
        self.created_layers.append(layer)
        
        self.canvas.setExtent(layer.extent())
        self.canvas.refresh()
        
        QMessageBox.information(self, "Sucesso", 
            "Círculo do objeto visível desenhado no mapa!")
    
    # ============ SLOTS - TAB PROJEÇÃO ============
    
    def calcular_projecao(self):
        """Calcula as coordenadas do ponto projetado"""
        lat = self.spinLatitudeProj.value()
        lon = self.spinLongitudeProj.value()
        azimute_mag = self.spinAzimute.value()
        distancia = self.spinDistancia.value()
        declinacao = self.spinDeclinacao.value()
        
        # Converter azimute magnético para verdadeiro
        azimute_verdadeiro = azimute_mag + declinacao
        
        # Normalizar para 0-360
        while azimute_verdadeiro < 0:
            azimute_verdadeiro += 360
        while azimute_verdadeiro >= 360:
            azimute_verdadeiro -= 360
        
        # Calcular ponto destino
        lat_alvo, lon_alvo = self.calcular_ponto_destino(
            lat, lon, azimute_verdadeiro, distancia
        )
        
        self.txtLatAlvo.setText(f"{lat_alvo:.6f}°")
        self.txtLngAlvo.setText(f"{lon_alvo:.6f}°")
        self.txtAzVerdadeiro.setText(f"{azimute_verdadeiro:.2f}°")
        
        QMessageBox.information(self, "Resultado", 
            f"Coordenadas do alvo:\n"
            f"Latitude: {lat_alvo:.6f}°\n"
            f"Longitude: {lon_alvo:.6f}°\n"
            f"Azimute Verdadeiro: {azimute_verdadeiro:.2f}°")
    
    def desenhar_projecao(self):
        """Desenha a linha e ponto da projeção no mapa"""
        lat = self.spinLatitudeProj.value()
        lon = self.spinLongitudeProj.value()
        azimute_mag = self.spinAzimute.value()
        distancia = self.spinDistancia.value()
        declinacao = self.spinDeclinacao.value()
        
        azimute_verdadeiro = azimute_mag + declinacao
        while azimute_verdadeiro < 0:
            azimute_verdadeiro += 360
        while azimute_verdadeiro >= 360:
            azimute_verdadeiro -= 360
        
        lat_alvo, lon_alvo = self.calcular_ponto_destino(
            lat, lon, azimute_verdadeiro, distancia
        )
        
        # Criar camada de linha
        line_layer = QgsVectorLayer("LineString?crs=EPSG:4326", 
                                    f"Projeção ({azimute_mag:.0f}° mag)", "memory")
        line_provider = line_layer.dataProvider()
        
        line_provider.addAttributes([
            QgsField("azimute_mag", QVariant.Double),
            QgsField("azimute_verd", QVariant.Double),
            QgsField("distancia_km", QVariant.Double)
        ])
        line_layer.updateFields()
        
        # Criar linha
        pontos = [QgsPointXY(lon, lat), QgsPointXY(lon_alvo, lat_alvo)]
        line_feature = QgsFeature()
        line_feature.setGeometry(QgsGeometry.fromPolylineXY(pontos))
        line_feature.setAttributes([azimute_mag, azimute_verdadeiro, distancia])
        
        line_provider.addFeature(line_feature)
        line_layer.updateExtents()
        
        # Estilizar linha
        line_symbol = QgsLineSymbol.createSimple({
            'color': '255,107,53',
            'width': '1',
            'line_style': 'dash'
        })
        line_layer.renderer().setSymbol(line_symbol)
        
        # Criar camada de pontos
        point_layer = QgsVectorLayer("Point?crs=EPSG:4326", 
                                     "Pontos Projeção", "memory")
        point_provider = point_layer.dataProvider()
        
        point_provider.addAttributes([
            QgsField("tipo", QVariant.String),
            QgsField("lat", QVariant.Double),
            QgsField("lon", QVariant.Double)
        ])
        point_layer.updateFields()
        
        # Ponto inicial
        point1 = QgsFeature()
        point1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        point1.setAttributes(["origem", lat, lon])
        
        # Ponto final
        point2 = QgsFeature()
        point2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon_alvo, lat_alvo)))
        point2.setAttributes(["alvo", lat_alvo, lon_alvo])
        
        point_provider.addFeatures([point1, point2])
        point_layer.updateExtents()
        
        # Estilizar pontos
        point_symbol = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '255,107,53',
            'size': '3',
            'outline_color': 'white',
            'outline_width': '0.5'
        })
        point_layer.renderer().setSymbol(point_symbol)
        
        # Adicionar ao projeto
        QgsProject.instance().addMapLayer(line_layer)
        QgsProject.instance().addMapLayer(point_layer)
        
        self.created_layers.extend([line_layer, point_layer])
        
        # Zoom para as camadas
        combined_extent = line_layer.extent()
        combined_extent.combineExtentWith(point_layer.extent())
        self.canvas.setExtent(combined_extent)
        self.canvas.refresh()
        
        QMessageBox.information(self, "Sucesso", 
            "Projeção desenhada no mapa!")
    
    # ============ SLOTS - TAB ANÉIS ============
    
    def desenhar_aneis(self):
        """Desenha anéis de distância no mapa"""
        lat = self.spinLatitudeAneis.value()
        lon = self.spinLongitudeAneis.value()
        num_aneis = self.spinNumAneis.value()
        intervalo_nm = self.spinIntervalo.value()
        mostrar_labels = self.checkMostrarLabels.isChecked()
        usar_gradiente = self.checkGradiente.isChecked()
        
        # Criar camada de polígonos
        layer = QgsVectorLayer("Polygon?crs=EPSG:4326", 
                              f"Anéis de Distância ({intervalo_nm} NM)", "memory")
        provider = layer.dataProvider()
        
        provider.addAttributes([
            QgsField("anel", QVariant.Int),
            QgsField("distancia_nm", QVariant.Double),
            QgsField("distancia_km", QVariant.Double)
        ])
        layer.updateFields()
        
        features = []
        
        for i in range(1, num_aneis + 1):
            dist_nm = i * intervalo_nm
            dist_km = dist_nm * self.NM_TO_KM
            raio_graus = dist_km / 111.0
            
            # Criar círculo
            pontos = []
            num_pontos = 64
            for j in range(num_pontos + 1):
                angulo = (360.0 / num_pontos) * j
                rad = math.radians(angulo)
                x = lon + raio_graus * math.cos(rad)
                y = lat + raio_graus * math.sin(rad)
                pontos.append(QgsPointXY(x, y))
            
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPolygonXY([pontos]))
            feature.setAttributes([i, dist_nm, dist_km])
            features.append(feature)
        
        provider.addFeatures(features)
        layer.updateExtents()
        
        # Estilizar com gradiente se solicitado
        if usar_gradiente:
            # Criar renderizador categorizado por anel
            from qgis.core import QgsCategorizedSymbolRenderer, QgsRendererCategory
            
            categories = []
            for i in range(1, num_aneis + 1):
                # Gradiente de verde (120°) para vermelho (0°)
                hue = 120 - (i * 120 / num_aneis)
                color = QColor.fromHsv(int(hue), 180, 200, 80)
                
                symbol = QgsFillSymbol.createSimple({
                    'color': f'{color.red()},{color.green()},{color.blue()},30',
                    'outline_color': f'{color.red()},{color.green()},{color.blue()}',
                    'outline_width': '0.3'
                })
                
                category = QgsRendererCategory(i, symbol, f"{i * intervalo_nm} NM")
                categories.append(category)
            
            renderer = QgsCategorizedSymbolRenderer('anel', categories)
            layer.setRenderer(renderer)
        else:
            # Estilo simples
            symbol = QgsFillSymbol.createSimple({
                'color': '0,255,245,20',
                'outline_color': '0,255,245',
                'outline_width': '0.3'
            })
            layer.renderer().setSymbol(symbol)
        
        # Adicionar labels se solicitado
        if mostrar_labels:
            from qgis.core import QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling
            from qgis.PyQt.QtGui import QFont
            
            label_settings = QgsPalLayerSettings()
            text_format = QgsTextFormat()
            
            font = QFont()
            font.setPointSize(8)
            font.setBold(True)
            text_format.setFont(font)
            text_format.setColor(QColor(0, 255, 245))
            text_format.setSize(8)
            
            buffer = text_format.buffer()
            buffer.setEnabled(True)
            buffer.setSize(0.5)
            buffer.setColor(QColor(0, 0, 0))
            text_format.setBuffer(buffer)
            
            label_settings.setFormat(text_format)
            label_settings.fieldName = "'Anel ' || anel || ' (' || distancia_nm || ' NM)'"
            label_settings.isExpression = True
            label_settings.enabled = True
            
            labeling = QgsVectorLayerSimpleLabeling(label_settings)
            layer.setLabelsEnabled(True)
            layer.setLabeling(labeling)
        
        # Adicionar ponto central
        point_layer = QgsVectorLayer("Point?crs=EPSG:4326", 
                                     "Centro Anéis", "memory")
        point_provider = point_layer.dataProvider()
        point_provider.addAttributes([
            QgsField("tipo", QVariant.String)
        ])
        point_layer.updateFields()
        
        point_feature = QgsFeature()
        point_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        point_feature.setAttributes(["centro"])
        point_provider.addFeature(point_feature)
        
        point_symbol = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '0,255,245',
            'size': '3',
            'outline_color': 'white',
            'outline_width': '0.5'
        })
        point_layer.renderer().setSymbol(point_symbol)
        
        # Adicionar ao projeto
        QgsProject.instance().addMapLayer(layer)
        QgsProject.instance().addMapLayer(point_layer)
        
        self.created_layers.extend([layer, point_layer])
        
        # Zoom
        self.canvas.setExtent(layer.extent())
        self.canvas.refresh()
        
        QMessageBox.information(self, "Sucesso", 
            f"{num_aneis} anéis desenhados no mapa!")
    
    # ============ SLOTS - TAB EXPORTAR ============
    
    def exportar_gpx(self):
        """Exporta as camadas criadas como GPX"""
        if not self.created_layers:
            QMessageBox.warning(self, "Aviso", 
                "Nenhuma camada foi criada ainda!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Salvar GPX", "", "GPS Exchange Format (*.gpx)")
        
        if filename:
            # GPX suporta apenas pontos, então vamos exportar apenas camadas de pontos
            point_layers = [l for l in self.created_layers 
                          if l.geometryType() == QgsWkbTypes.PointGeometry]
            
            if not point_layers:
                QMessageBox.warning(self, "Aviso", 
                    "Nenhuma camada de pontos para exportar!")
                return
            
            for layer in point_layers:
                QgsVectorFileWriter.writeAsVectorFormat(
                    layer, filename, "UTF-8", layer.crs(), "GPX",
                    layerOptions=['GPX_USE_EXTENSIONS=YES'])
            
            QMessageBox.information(self, "Sucesso", 
                f"Arquivo GPX salvo em:\n{filename}")
    
    def exportar_kml(self):
        """Exporta as camadas criadas como KML"""
        if not self.created_layers:
            QMessageBox.warning(self, "Aviso", 
                "Nenhuma camada foi criada ainda!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Salvar KML", "", "Keyhole Markup Language (*.kml)")
        
        if filename:
            for i, layer in enumerate(self.created_layers):
                output = filename if i == 0 else filename.replace('.kml', f'_{i}.kml')
                QgsVectorFileWriter.writeAsVectorFormat(
                    layer, output, "UTF-8", layer.crs(), "KML")
            
            QMessageBox.information(self, "Sucesso", 
                f"Arquivo(s) KML salvo(s)!")
    
    def exportar_shapefile(self):
        """Exporta as camadas criadas como Shapefile"""
        if not self.created_layers:
            QMessageBox.warning(self, "Aviso", 
                "Nenhuma camada foi criada ainda!")
            return
        
        directory = QFileDialog.getExistingDirectory(
            self, "Selecionar Diretório para Shapefiles")
        
        if directory:
            for layer in self.created_layers:
                filename = os.path.join(directory, f"{layer.name()}.shp")
                QgsVectorFileWriter.writeAsVectorFormat(
                    layer, filename, "UTF-8", layer.crs(), "ESRI Shapefile")
            
            QMessageBox.information(self, "Sucesso", 
                f"Shapefiles salvos em:\n{directory}")
    
    def exportar_geojson(self):
        """Exporta as camadas criadas como GeoJSON"""
        if not self.created_layers:
            QMessageBox.warning(self, "Aviso", 
                "Nenhuma camada foi criada ainda!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Salvar GeoJSON", "", "GeoJSON (*.geojson *.json)")
        
        if filename:
            for i, layer in enumerate(self.created_layers):
                output = filename if i == 0 else filename.replace('.geojson', f'_{i}.geojson').replace('.json', f'_{i}.json')
                QgsVectorFileWriter.writeAsVectorFormat(
                    layer, output, "UTF-8", layer.crs(), "GeoJSON")
            
            QMessageBox.information(self, "Sucesso", 
                f"Arquivo(s) GeoJSON salvo(s)!")
    
    def limpar_camadas(self):
        """Remove todas as camadas criadas pelo plugin"""
        if not self.created_layers:
            QMessageBox.information(self, "Info", 
                "Nenhuma camada para limpar!")
            return
        
        reply = QMessageBox.question(self, "Confirmar", 
            f"Deseja remover {len(self.created_layers)} camada(s) criada(s)?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for layer in self.created_layers:
                QgsProject.instance().removeMapLayer(layer.id())
            
            self.created_layers.clear()
            self.canvas.refresh()
            
            QMessageBox.information(self, "Sucesso", 
                "Todas as camadas foram removidas!")
