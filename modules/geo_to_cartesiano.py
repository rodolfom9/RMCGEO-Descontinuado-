# -*- coding: utf-8 -*-
"""
/***************************************************************************
 classnomeDialog
                                 A QGIS plugin
 descricao
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2025-03-20
        git sha              : $Format:%H$
        copyright            : (C) 2025 by rodolfo
        email                : email
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QApplication, QMessageBox
from qgis.PyQt.QtGui import QIcon, QPalette, QColor
from qgis.PyQt.QtCore import Qt
import math
from qgis.core import QgsApplication

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'cartesiana-geodesica.ui'))


class GmsToCartesiano(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None, iface=None):
        """Constructor."""
        super(GmsToCartesiano, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.setup_ui()
        self.setup_connections()
        self.apply_modern_style()

    def setup_ui(self):
        """Configura a interface inicial."""
        try:
            self.clipboard = QApplication.clipboard()
            self.setWindowTitle("Conversor de Coordenadas Geodésicas para Cartesianas")
            
            # Configurar tooltips mais informativos
            self.lat_input.setToolTip("Digite a latitude em GMS (ex: 23 30 45) ou decimal\nValores válidos: -90° a 90°")
            self.lon_input.setToolTip("Digite a longitude em GMS (ex: 46 15 30) ou decimal\nValores válidos: -180° a 180°")
            self.alt_input.setToolTip("Digite a altitude em metros\nValores válidos: -10000m a 100000m")
            
            # Configurar ícones
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', 'copy.png')
            if os.path.exists(icon_path):
                self.copyqline_x.setIcon(QIcon(icon_path))
                self.copyqline_y.setIcon(QIcon(icon_path))
                self.copyqline_z.setIcon(QIcon(icon_path))
            else:
                # Fallback para ícones padrão do QGIS
                self.copyqline_x.setIcon(QIcon(':/images/themes/default/mActionEditCopy.svg'))
                self.copyqline_y.setIcon(QIcon(':/images/themes/default/mActionEditCopy.svg'))
                self.copyqline_z.setIcon(QIcon(':/images/themes/default/mActionEditCopy.svg'))
            
            # Configurar botões
            self.buttonconvertg.setText("Converter")
            self.buttonconvertd.setText("Converter")
            
            # Configurar campos de saída como somente leitura
            self.x_output.setReadOnly(True)
            self.y_output.setReadOnly(True)
            self.z_output.setReadOnly(True)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao inicializar a interface: {str(e)}")

    def setup_connections(self):
        """Configura as conexões dos sinais."""
        self.buttonconvertg.clicked.connect(self.atualizar_coordenadas_gms)
        self.buttonconvertd.clicked.connect(self.atualizar_coordenadas_decimal)
        self.copyqline_x.clicked.connect(self.copy_x)
        self.copyqline_y.clicked.connect(self.copy_y)
        self.copyqline_z.clicked.connect(self.copy_z)

    def apply_modern_style(self):
        """Aplica um estilo moderno à interface."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QLineEdit:read-only {
                background-color: #f5f5f5;
            }
            QPushButton {
                padding: 5px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QToolButton {
                background-color: transparent;
                border: none;
            }
            QLabel {
                color: #333;
            }
        """)

    def validate_coordinates(self, lat, lon, alt):
        """Valida os valores das coordenadas."""
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude deve estar entre -90° e 90°")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude deve estar entre -180° e 180°")
        if not (-10000 <= alt <= 100000):
            raise ValueError("Altitude deve estar entre -10000m e 100000m")

    def geografica_para_cartesiana(self, lat, lon, alt):
        """Converte coordenadas geográficas para cartesianas."""
        try:
            self.validate_coordinates(lat, lon, alt)
            
            a = 6378137.0  # Semi-eixo maior (metros)
            f = float(1 / 298.257222101)  # Achatamento
            e2 = (2 * f) - (f ** 2)  # Excentricidade ao quadrado

            lat_rad = math.radians(float(lat))
            lon_rad = math.radians(float(lon))

            N = a / math.sqrt(1 - e2 * math.sin(lat_rad) ** 2)
            x = (N + float(alt)) * math.cos(lat_rad) * math.cos(lon_rad)
            y = (N + float(alt)) * math.cos(lat_rad) * math.sin(lon_rad)
            z = ((1 - e2) * N + float(alt)) * math.sin(lat_rad)
            
            return x, y, z
        except ValueError as e:
            raise ValueError(f"Erro na conversão: {str(e)}")

    def atualizar_coordenadas_gms(self):
        """Atualiza as coordenadas a partir do formato GMS."""
        try:
            lat = self.lat_input.text() or "0"
            lon = self.lon_input.text() or "0"
            alt = self.alt_input.text() or "0"

            if " " in lat:
                lat = self.gms_para_decimal(lat)
            else:
                lat = float(lat)
            if " " in lon:
                lon = self.gms_para_decimal(lon)
            else:
                lon = float(lon)
            alt = float(alt)

            x, y, z = self.geografica_para_cartesiana(lat, lon, alt)
            self.x_output.setText(f"{x:.3f}")
            self.y_output.setText(f"{y:.3f}")
            self.z_output.setText(f"{z:.3f}")
            
            self.iface.statusBarIface().showMessage("Conversão realizada com sucesso!", 3000)
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))

    def atualizar_coordenadas_decimal(self):
        """Atualiza as coordenadas a partir do formato decimal."""
        try:
            latd = self.latd_input.text() or "0"
            lond = self.lond_input.text() or "0"
            altd = self.altd_input.text() or "0"

            latd = float(latd)
            lond = float(lond)
            altd = float(altd)

            x, y, z = self.geografica_para_cartesiana(latd, lond, altd)
            self.x_output.setText(f"{x:.3f}")
            self.y_output.setText(f"{y:.3f}")
            self.z_output.setText(f"{z:.3f}")
            
            self.iface.statusBarIface().showMessage("Conversão realizada com sucesso!", 3000)
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))

    def gms_para_decimal(self, gms_str):
        """Converte coordenada GMS para decimal."""
        try:
            partes = gms_str.strip().split()
            if len(partes) != 3:
                raise ValueError("Formato inválido! Use: 'grau minuto segundo'")
            
            graus, minutos, segundos = map(float, partes)
            sinal = -1 if graus < 0 else 1
            decimal = abs(graus) + (minutos / 60) + (segundos / 3600)
            return sinal * decimal
        except ValueError as e:
            raise ValueError(f"Erro na conversão GMS: {str(e)}")

    def copy_x(self):
        """Copia a coordenada X para a área de transferência."""
        self.copy_to_clipboard(self.x_output.text(), "X")

    def copy_y(self):
        """Copia a coordenada Y para a área de transferência."""
        self.copy_to_clipboard(self.y_output.text(), "Y")

    def copy_z(self):
        """Copia a coordenada Z para a área de transferência."""
        self.copy_to_clipboard(self.z_output.text(), "Z")

    def copy_to_clipboard(self, text, coord):
        """Copia texto para a área de transferência."""
        if text:
            self.clipboard.setText(text)
            self.iface.statusBarIface().showMessage(f"Coordenada {coord} copiada: {text}", 3000)

    def reset_fields(self):
        """Redefine todos os campos."""
        self.lat_input.clear()
        self.lon_input.clear()
        self.alt_input.clear()
        self.latd_input.clear()
        self.lond_input.clear()
        self.altd_input.clear()
        self.x_output.clear()
        self.y_output.clear()
        self.z_output.clear()

def run(iface):
    """Executa o diálogo de conversão."""
    try:
        # Garantir que o caminho da aplicação está inicializado
        if not QgsApplication.instance():
            QgsApplication.setPrefixPath("/usr", True)
            QgsApplication.initQgis()
        
        dlg = GmsToCartesiano(iface=iface)
        dlg.reset_fields()
        dlg.show()
        dlg.exec_()
    except Exception as e:
        iface.messageBar().pushCritical("Erro", f"Erro ao executar o plugin: {str(e)}")

def unload():
    """Limpa recursos quando o plugin é descarregado."""
    try:
        if QgsApplication.instance():
            QgsApplication.exitQgis()
    except:
        pass